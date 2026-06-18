# sources/control-plane/csi-driver-iscsi/pkg/iscsilib/iscsiadm.go

Purpose: provides the narrow `iscsiadm` command facade and CHAP configuration helpers used by the connector lifecycle.

Important APIs and types: `Secrets` carries CHAP `SecretsType`, username/password, and optional bidirectional username/password fields. Public command helpers include `ListInterfaces`, `ShowInterface`, `CreateDBEntry`, `Discoverydb`, `GetSessions`, `Login`, `Logout`, `DeleteDBEntry`, and `DeleteIFace`. Internal helpers `iscsiCmd`, `iscsiadmDebug`, and `createCHAPEntries` centralize timeout execution, logging, and `iscsiadm -o update` argument construction.

Control flow: every public helper builds a specific `iscsiadm` mode/action invocation and delegates to `iscsiCmd`. `CreateDBEntry` creates a node entry for IQN/portal/interface and then applies discovery and session CHAP settings when the corresponding secret type is `chap`. `Discoverydb` creates a sendtargets discoverydb entry, optionally applies discovery CHAP, runs `--discover`, and deletes the discoverydb entry on discovery failure. `Login` logs in and deletes the node DB entry if login fails.

State and persistence: state is persisted by open-iscsi in its node, iface, and discovery databases rather than in this package. The helper logs command output with newlines escaped. Secret values are passed as command-line arguments, which can expose them to process inspection and verbose logs if callers are not careful.

Dependencies and integration: uses `ExecWithTimeout` through the package-level `execWithTimeout` hook, Linux `iscsiadm`, and `klog`. It is called by `iscsi.go` for discovery, login, session listing, interface inspection, logout, and cleanup.

Risks: command timeout is fixed at three seconds for all `iscsiadm` operations. CHAP is keyed by the exact string `chap`; other auth names are ignored. `Login` reports a sendtargets-style error message although it is logging in. Secrets are embedded in argv for `iscsiadm -v`.

Test signals: no direct tests are present, but the command execution hook makes the API suitable for unit tests that assert arguments and error handling.
