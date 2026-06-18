# Group Research: subset-b-008175

This grouped report covers MinIO `mc` IDP, ILM, legalhold, license, and list command sources. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-list.go -->
# Research: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-list.go

Purpose: implements `mc idp ldap accesskey list`/`ls`, listing LDAP users and their associated STS and service-account access keys.

Important APIs/types/functions: `idpLdapAccesskeyListFlags`, `idpLdapAccesskeyListCmd`, `mainIDPLdapAccesskeyList`, and shared `commonAccesskeyList`. The command calls `madmin.AdminClient.ListAccessKeysLDAPBulkWithOpts` and prints `userAccesskeyList` messages with `LDAP: true`.

Control flow: `commonAccesskeyList` validates arguments, parses `TARGET[:CFGNAME]`, resolves users and list flags, and creates `madmin.ListAccessKeysOpts`. With no user, `--self`, or `--all`, it tentatively sets `All` and allows an Access Denied retry as self for backward compatibility. `mainIDPLdapAccesskeyList` creates an admin client, calls the LDAP bulk listing API, retries if needed, and prints one message per DN.

State and persistence: read-only against MinIO server identity data. No local persistence.

Dependencies/integration points: relies on `newAdminClient`, `globalContext`, `fatalIf`, `probe`, `madmin.ListAccessKeysOpts`, and shared output types from other access-key files.

Risks: flag error text says `--permanent-only` while the actual flag is `--svcacc-only`; exact string matching on `"Access Denied."` is brittle. `commonAccesskeyList` is shared by OpenID, so changes affect both IDP families.

Test signals: no direct tests in this file; coverage should exercise flag exclusivity, target config-name parsing, tentative all retry, and LDAP message shape.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-remove.go -->
# Research: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-remove.go

Purpose: implements `mc idp ldap accesskey remove`/`rm`, deleting an LDAP-linked service account access key.

Important APIs/types/functions: `idpLdapAccesskeyRemoveCmd`, `mainIDPLdapAccesskeyRemove`, and shared `commonAccesskeyRemove`. It uses `madmin.AdminClient.DeleteServiceAccount` and emits `accesskeyMessage`.

Control flow: validates exactly two arguments, target and access key. It creates an admin client for the target alias, deletes the service account by access key, and prints a success message.

State and persistence: mutates server-side service-account state. It does not alter local config.

Dependencies/integration points: shared with OpenID remove through `commonAccesskeyRemove`; uses common CLI globals and admin-client setup.

Risks: the helper intentionally has no LDAP-specific validation, so it will delete any service account visible to the credentials. Callers depend on command path and server authorization to scope behavior.

Test signals: no direct tests; useful tests would mock `DeleteServiceAccount` and validate arity and message emission.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-sts-revoke.go -->
# Research: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-sts-revoke.go

Purpose: implements `mc idp ldap accesskey sts-revoke`, revoking STS tokens for an LDAP user or for the authenticated LDAP service account.

Important APIs/types/functions: `idpLdapAccesskeySTSRevokeCmd` and `mainIdpLdapAccesskeySTSRevoke`. It reuses `adminAccesskeySTSRevokeFlags`, `checkSTSRevokeSyntax`, and `stsRevokeMessage` from admin access-key code, then calls `madmin.AdminClient.RevokeTokens`.

Control flow: validates syntax, extracts alias, optional user, `--token-type`, and `--all`, creates an admin client, sends `madmin.RevokeTokensReq`, and prints token-revoke output.

State and persistence: mutates server-side STS token state by invalidating matching tokens. No local persistence.

Dependencies/integration points: tied to shared admin access-key revoke validation and message types; operates through MinIO admin API.

Risks: broad `--all` revocation is destructive for active sessions. Empty user is meaningful for `--self`, so validation in the shared helper is critical.

Test signals: no local tests; should cover `--all` versus `--token-type`, `--self`, non-self user, and request payload shape.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-sts-revoke.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey.go -->
# Research: sources/object-store/minio-mc/cmd/idp-ldap-accesskey.go

Purpose: registers the `mc idp ldap accesskey` command namespace.

Important APIs/types/functions: `idpLdapAccesskeySubcommands`, `idpLdapAccesskeyCmd`, and `mainIDPLDAPAccesskey`. The namespace includes list, remove, info, create, create-with-login, edit, enable, disable, and STS revoke.

Control flow: CLI framework dispatches to subcommands. If invoked without a matching subcommand, `mainIDPLDAPAccesskey` delegates to `commandNotFound`.

State and persistence: no direct state changes. Persistence is delegated to subcommands.

Dependencies/integration points: depends on subcommand variables declared across LDAP access-key files, `globalFlags`, and `setGlobalsFromContext`.

Risks: adding or removing a subcommand here directly changes CLI discoverability. Hidden or missing commands can make implemented functionality unreachable.

Test signals: no direct tests; smoke tests should assert command registration and help output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-policy-subcommands.go -->
# Research: sources/object-store/minio-mc/cmd/idp-ldap-policy-subcommands.go

Purpose: implements LDAP policy association commands: attach, detach, and entities.

Important APIs/types/functions: `mainIDPLdapPolicyAttach`, `mainIDPLdapPolicyDetach`, `mainIDPLdapPolicyEntities`, `policyAssociationMessage`, `policyEntities`, `iFmt`, and `builderWrapper`. Admin calls are `AttachPolicyLDAP`, `DetachPolicyLDAP`, and `GetLDAPPolicyEntities`.

Control flow: attach requires target plus at least one policy and constructs `madmin.PolicyAssociationReq`, relying on `req.IsValid()` to enforce exactly one entity. Detach performs its own missing-entity check and calls server detach. Entities accepts repeated `--user`, `--group`, and `--policy` filters, fetches mappings, and renders user, group, policy, group membership, and effective-policy sections.

State and persistence: attach/detach mutate server-side LDAP policy mappings. Entities is read-only.

Dependencies/integration points: integrates with `madmin.PolicyEntitiesResult`, `lipgloss`, `colorjson`, and MinIO set utilities for effective-policy calculation.

Risks: detach does not call `PolicyAssociationReq.IsValid`, so multiple entity flags may reach the server depending on server validation. Text wrapping is display-only and must not be treated as a parseable API.

Test signals: no direct tests; useful coverage includes attach/detach validation, entities formatting with group membership, and JSON output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-policy-subcommands.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-policy.go -->
# Research: sources/object-store/minio-mc/cmd/idp-ldap-policy.go

Purpose: registers `mc idp ldap policy` as the LDAP policy assignment namespace.

Important APIs/types/functions: `idpLdapPolicySubcommands`, `idpLdapPolicyCmd`, and `mainIDPLDAPPolicy`.

Control flow: CLI dispatches to attach, detach, and entities. Unknown or absent subcommands route through `commandNotFound`.

State and persistence: no direct state changes.

Dependencies/integration points: depends on policy subcommand definitions, `globalFlags`, and common command setup.

Risks: namespace wiring is simple, but missing entries make implemented policy operations unreachable.

Test signals: no direct tests; command registration/help tests are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-subcommands.go -->
# Research: sources/object-store/minio-mc/cmd/idp-ldap-subcommands.go

Purpose: implements LDAP IDP configuration add, update, remove, list, info, enable, and disable commands.

Important APIs/types/functions: `mainIDPLDAPAdd`, `mainIDPLDAPUpdate`, `mainIDPLDAPRemove`, `mainIDPLDAPList`, `mainIDPLDAPInfo`, `mainIDPLDAPEnable`, and `mainIDPLDAPDisable`. It reuses OpenID-shared helpers `idpRemove`, `idpListCommon`, `idpInfo`, and `idpEnableDisable`.

Control flow: add/update parse `TARGET [CFG_PARAMS...]`, enforce LDAP default config only, join remaining `key=value` parameters into a config body, and call `AddOrUpdateIDPConfig` with `madmin.LDAPIDPCfg`. Remove/list/info require one target and call shared helpers. Enable/disable also require one target and write `enable=` or `enable=off` through the shared helper.

State and persistence: mutates MinIO server IDP configuration. Server may return a restart requirement, surfaced via `configSetMessage`.

Dependencies/integration points: depends on `madmin.LDAPIDPCfg`, admin-client creation, shared IDP helpers, and global CLI setup.

Risks: this file rejects named LDAP configs by design, so future server support for named LDAP configs requires coordinated changes. Joining raw args into one config string preserves existing config API behavior but makes shell quoting important.

Test signals: no direct tests; important cases include named-config rejection, update versus add flag, and restart message propagation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-subcommands.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap.go -->
# Research: sources/object-store/minio-mc/cmd/idp-ldap.go

Purpose: registers the `mc idp ldap` namespace.

Important APIs/types/functions: `idpLdapSubcommands`, `idpLdapCmd`, and `mainIDPLdap`. The namespace includes configuration, policy, and access-key commands.

Control flow: normal CLI subcommand dispatch, with `commandNotFound` fallback.

State and persistence: no direct state changes.

Dependencies/integration points: integrates LDAP command groups under the top-level IDP command.

Risks: this file is the discoverability point for LDAP policy and access-key functionality; omission breaks CLI reachability.

Test signals: no direct tests; command-tree smoke tests should validate subcommand registration.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey-disable.go -->
# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey-disable.go

Purpose: implements `mc idp openid accesskey disable`.

Important APIs/types/functions: `idpOpenidAccesskeyDisableCmd` and `mainIDPOpenIDAccesskeyDisable`, which delegates to shared `enableDisableAccesskey(ctx, false)`.

Control flow: CLI validation and actual server mutation happen in the shared helper from LDAP access-key enable/disable code. This wrapper supplies OpenID command metadata and help.

State and persistence: disables a service account/access key server-side through shared admin APIs.

Dependencies/integration points: depends on global command setup and shared access-key enable/disable implementation.

Risks: help examples say LDAP even though this is OpenID, which can confuse users. Behavior is shared with LDAP and not OpenID-specific.

Test signals: no direct tests; should verify command path delegates with `enable=false`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey-disable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey-edit.go -->
# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey-edit.go

Purpose: implements `mc idp openid accesskey edit`.

Important APIs/types/functions: `idpOpenIDAccesskeyEditFlags`, `idpOpenidAccesskeyEditCmd`, and `mainIDPOpenIDAccesskeyEdit`, delegating to `commonAccesskeyEdit`.

Control flow: this file declares editable attributes: secret key, policy file, friendly name, description, expiry duration, and absolute expiry. The shared helper validates args, builds `madmin.UpdateServiceAccountReq`, and calls the admin API.

State and persistence: mutates server-side service-account metadata and credentials.

Dependencies/integration points: shared with LDAP edit. It relies on policy-file reading and expiry parsing in the common helper.

Risks: secret-key changes are sensitive and may break clients. Help uses generic `[TARGET]` wording, so shared helper validation must remain authoritative.

Test signals: no direct tests; exercise each flag and mutual expiry handling in shared helper tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey-edit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey-enable.go -->
# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey-enable.go

Purpose: implements `mc idp openid accesskey enable`.

Important APIs/types/functions: `idpOpenidAccesskeyEnableCmd` and `mainIDPOpenIDAccesskeyEnable`, delegating to `enableDisableAccesskey(ctx, true)`.

Control flow: wrapper registers the command, then the shared helper validates target/access key and updates status on the server.

State and persistence: enables an access key server-side.

Dependencies/integration points: shared access-key enable/disable helper and MinIO admin API.

Risks: help example says LDAP; actual behavior is OpenID namespace but backend operation is provider-neutral.

Test signals: no direct tests; command-level test should assert `enable=true` delegation and output message.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey-enable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey-info.go -->
# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey-info.go

Purpose: implements `mc idp openid accesskey info`, showing OpenID identity metadata for access keys.

Important APIs/types/functions: `idpOpenidAccesskeyInfoCmd`, `openIDAccessKeyInfo`, `openIDAccessKeyInfo.String`, and `mainIDPOpenIDAccesskeyInfo`.

Control flow: command requires target and one or more access keys, then delegates lookup to `commonAccesskeyInfo`. The display type renders config name, display-name claim/value when present, and user ID claim/value; default config `_` is shown as `_ (default)`.

State and persistence: read-only against server-side access-key metadata.

Dependencies/integration points: depends on shared info helper and `iFmt` from LDAP policy formatting.

Risks: OpenID output differs from LDAP info shape, so shared helper must select the right message type. Claim labels come from server data and should be treated as display text.

Test signals: no direct tests; should cover default config formatting, missing display-name claim, and JSON output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey-list.go -->
# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey-list.go

Purpose: implements `mc idp openid accesskey list`/`ls`, listing OpenID users and their STS/service-account access keys.

Important APIs/types/functions: `idpOpenIDAccesskeyListFlags`, `openIDAccesskeyList`, and `mainIDPOpenIDAccesskeyList`. It reuses `commonAccesskeyList` and calls `ListAccessKeysOpenIDBulk`.

Control flow: common parsing supports target config names and `--all-configs`. The command calls the OpenID bulk listing API, retries Access Denied tentative-all as self, then prints one message per OpenID config. The string renderer shows config name, MinIO access key, external ID, readable name, and keys with humanized expiry and STS marker.

State and persistence: read-only server query.

Dependencies/integration points: madmin OpenID access-key list types, humanize time formatting, lipgloss, colorjson, and shared access-key parser.

Risks: shares LDAP-oriented flag names such as `users-only` and common error strings; exact Access Denied string matching is brittle. Output contains relative expiry text in console mode, so scripts should use JSON.

Test signals: no direct tests; should cover all-configs, config suffix parsing, list filters, and mixed STS/service accounts.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey-remove.go -->
# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey-remove.go

Purpose: implements `mc idp openid accesskey remove`/`rm`.

Important APIs/types/functions: `idpOpenidAccesskeyRemoveCmd` and `mainIDPOpenIDAccesskeyRemove`, delegating to `commonAccesskeyRemove`.

Control flow: wrapper registers help and command metadata. Shared helper validates target plus access key, creates admin client, deletes the service account, and prints success.

State and persistence: deletes a server-side service account access key.

Dependencies/integration points: same backend as LDAP access-key remove through `DeleteServiceAccount`.

Risks: provider-neutral deletion means the command path does not itself verify OpenID ownership; server authorization and access-key identity decide outcome.

Test signals: no direct tests; shared remove behavior should be tested once and command wiring smoke-tested.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey.go -->
# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey.go

Purpose: registers `mc idp openid accesskey`.

Important APIs/types/functions: `idpOpenidAccesskeySubcommands`, `idpOpenIDAccesskeyCmd`, and `mainIDPOpenIDAccesskey`.

Control flow: dispatches to list, remove, info, edit, enable, or disable; unknown commands route to `commandNotFound`.

State and persistence: none directly.

Dependencies/integration points: integrates OpenID access-key wrappers under OpenID IDP command.

Risks: no create command is included for OpenID here, unlike LDAP; that is a product/CLI surface distinction.

Test signals: command-tree tests should verify the intended subcommand set.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-accesskey.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-subcommands.go -->
# Research: sources/object-store/minio-mc/cmd/idp-openid-subcommands.go

Purpose: implements OpenID IDP configuration add, update, remove, list, info, enable, and disable, plus shared helpers used by LDAP.

Important APIs/types/functions: `mainIDPOpenIDAddOrUpdate`, `idpRemove`, `idpListCommon`, `idpCfgList`, `idpInfo`, `idpConfig`, and `idpEnableDisable`. Admin APIs include `AddOrUpdateIDPConfig`, `DeleteIDPConfig`, `ListIDPConfig`, and `GetIDPConfig`.

Control flow: add/update parse optional config name when the second arg lacks `=`, join config params, and call OpenID config update. Remove/info/enable/disable accept optional config name. Shared helpers switch between `madmin.OpenidIDPCfg` and `madmin.LDAPIDPCfg`. Listing and info render boxed lipgloss tables, with `_` treated as default config.

State and persistence: add/update/delete/enable/disable mutate server IDP config and may require restart; list/info are read-only.

Dependencies/integration points: central IDP helper implementation for both OpenID and LDAP command files.

Risks: `idpEnableDisable` uses error text saying "remove" even for enable/disable failure. The config body is raw joined CLI input, so quoting and value spaces matter.

Test signals: no direct tests; cover config-name parsing, default `_` rendering, env-origin info markers, and helper behavior for LDAP versus OpenID.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid-subcommands.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid.go -->
# Research: sources/object-store/minio-mc/cmd/idp-openid.go

Purpose: registers the `mc idp openid` command namespace.

Important APIs/types/functions: `idpOpenidSubcommands`, `idpOpenidCmd`, and `mainIDPOpenID`.

Control flow: command dispatches to OpenID config and access-key subcommands, with unknown command fallback.

State and persistence: no direct state changes.

Dependencies/integration points: child of top-level `idp`; includes a TODO for future OpenID policy commands.

Risks: namespace omissions make implemented OpenID operations unreachable. The TODO signals policy parity is not implemented.

Test signals: command registration/help tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-openid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp.go -->
# Research: sources/object-store/minio-mc/cmd/idp.go

Purpose: top-level command registration for MinIO identity provider management.

Important APIs/types/functions: `idpSubcommands`, `idpCmd`, and `mainIDP`.

Control flow: routes `mc idp` to OpenID or LDAP namespaces, otherwise calls `commandNotFound`.

State and persistence: no direct state changes.

Dependencies/integration points: hooks IDP command tree into the wider `mc` CLI.

Risks: very small but critical command registration file; missing subcommands hide entire IDP feature groups.

Test signals: command-tree smoke tests should assert `openid` and `ldap` are present.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-deprecated-cmds.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-deprecated-cmds.go

Purpose: preserves hidden legacy `mc ilm add/rm/edit/ls/export/import` entry points while the visible command surface uses `mc ilm rule ...`.

Important APIs/types/functions: `ilmDepCmds` and hidden command variables `ilmDepAddCmd`, `ilmDepRmCmd`, `ilmDepEditCmd`, `ilmDepLsCmd`, `ilmDepExportCmd`, `ilmDepImportCmd`.

Control flow: each deprecated command points to the same handler and flags as the newer rule subcommand. `Hidden: true` keeps them out of normal help output while retaining compatibility.

State and persistence: no direct state changes here; handlers mutate or read bucket lifecycle configuration.

Dependencies/integration points: depends on ILM rule handlers and flags declared in rule files.

Risks: compatibility wrappers can drift from current help text or flag behavior if new rule flags are not reused. Hidden commands still affect CLI behavior and should be tested before removal.

Test signals: no direct tests; backward-compatibility CLI tests should assert hidden aliases still work.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-deprecated-cmds.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-main.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-main.go

Purpose: registers the top-level `mc ilm` namespace and shared display color names.

Important APIs/types/functions: `ilmSubcommands`, `ilmCmd`, `mainILM`, constants for color themes, and `setILMDisplayColorScheme`.

Control flow: dispatches visible subcommands `rule`, `tier`, and `restore`, plus hidden deprecated commands. `setILMDisplayColorScheme` configures console colors used by rule output.

State and persistence: no server or local persistence. It only configures CLI routing and console color state.

Dependencies/integration points: depends on rule, tier, restore, and deprecated command variables.

Risks: color theme names are referenced across ILM files; renaming breaks formatting. Hidden deprecated commands are appended to the main command and remain runnable.

Test signals: command-tree smoke tests and simple color setup coverage if console output tests exist.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-remove.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-remove.go

Purpose: implements `mc ilm rule remove`/`rm`, removing one lifecycle rule by ID or all rules with explicit force.

Important APIs/types/functions: `ilmRemoveFlags`, `ilmRmCmd`, `ilmRmMessage`, `checkILMRemoveSyntax`, and `mainILMRemove`.

Control flow: syntax requires one target. `--all` and `--force` must be supplied together; otherwise `--id` is required. The handler fetches current lifecycle config, either clears `Rules` or calls `ilm.RemoveILMRule`, writes back with `SetLifecycle`, and prints success.

State and persistence: mutates bucket lifecycle configuration on the target server.

Dependencies/integration points: uses `newClient`, MinIO client `GetLifecycle`/`SetLifecycle`, and helper package `cmd/ilm`.

Risks: `--all --force` clears all rules. Removal is read-modify-write and can overwrite concurrent lifecycle changes. Empty config semantics depend on server `SetLifecycle`.

Test signals: no direct tests; helper `RemoveILMRule` deserves unit coverage for nil/empty/not found. CLI tests should verify force coupling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-restore.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-restore.go

Purpose: implements `mc ilm restore`, restoring archived objects from remote tier back to hot storage for a limited number of days.

Important APIs/types/functions: `ilmRestoreFlags`, `checkILMRestoreSyntax`, `restoreObject`, `sendRestoreRequests`, `waitRestoreObject`, `checkRestoreStatus`, `showRestoreStatus`, and `mainILMRestore`.

Control flow: validates one target, positive `--days`, and incompatible version flags. For a single object it sends one restore request; for recursive mode it lists objects, optionally with versions, and sends restore calls per content. It then polls `Stat` until restore is no longer ongoing, showing progress or JSON summary.

State and persistence: sends S3 restore requests, creating temporary restored copies server-side. Does not persist local state.

Dependencies/integration points: MinIO client `Restore`, `List`, and `Stat`; SSE-C parsing through `validateAndCreateEncryptionKeys` and `getSSE`.

Risks: polling loops have no timeout beyond process cancellation. Recursive restore can issue many requests and waits sequentially during status checks. Version syntax check incorrectly uses `ctx.Bool("version-id")` for a string flag, which should be reviewed.

Test signals: no direct tests; should cover syntax matrix, recursive list behavior, SSE-C stat options, and JSON progress output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-restore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-rule-add.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-rule-add.go

Purpose: implements `mc ilm rule add`, adding lifecycle expiration, transition, and noncurrent-version actions to a bucket.

Important APIs/types/functions: `ilmAddCmd`, `ilmAddFlags`, `ilmAddMessage`, `checkILMAddSyntax`, and `mainILMAdd`.

Control flow: validates one target, fetches existing lifecycle config, treats `NoSuchLifecycleConfiguration` as an empty config, parses CLI flags into `ilm.LifecycleOptions`, converts them to a validated `lifecycle.Rule`, appends the rule, writes via `SetLifecycle`, and prints the generated or supplied rule ID.

State and persistence: mutates bucket lifecycle configuration server-side.

Dependencies/integration points: relies heavily on `cmd/ilm` parsing and validation helpers, MinIO `lifecycle` types, and `minio.ToErrorResponse` for absent config.

Risks: read-append-write can race with concurrent lifecycle edits. Deprecated and current flags coexist, so parser changes must preserve compatibility. Generated IDs are xid strings.

Test signals: parser unit tests exist for filters; CLI-level add should be tested with no existing config and representative action combinations.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-rule-add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-rule-edit.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-rule-edit.go

Purpose: implements `mc ilm rule edit`, modifying fields on an existing lifecycle rule.

Important APIs/types/functions: `ilmEditCmd`, `ilmEditFlags`, `ilmEditMessage`, `checkILMEditSyntax`, and `mainILMEdit`.

Control flow: requires one target and non-empty `--id`. It fetches lifecycle config, parses edit options, locates the matching rule by ID, applies non-nil option fields through `ilm.ApplyRuleFields`, writes the full config back, and prints success.

State and persistence: mutates bucket lifecycle configuration server-side.

Dependencies/integration points: shared add flags, `cmd/ilm` option parsing and field application, MinIO lifecycle API.

Risks: if no lifecycle config exists, it creates an empty config but then fails to find the rule, which is correct but indirect. Field application resets some mutually exclusive fields and can leave others unchanged by design; tests must protect this partial-update contract.

Test signals: no direct tests for edit; should cover enable/disable, date versus days reset, missing ID, and not-found rule behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-rule-edit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-rule-export.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-rule-export.go

Purpose: implements `mc ilm rule export`, printing bucket lifecycle configuration as JSON.

Important APIs/types/functions: `ilmExportCmd`, `ilmExportMessage`, `checkILMExportSyntax`, and `mainILMExport`.

Control flow: validates one target, creates a client, fetches lifecycle config and updated timestamp, errors when no rules exist, and prints either raw config in console mode or wrapped status/target/config JSON in JSON mode.

State and persistence: read-only server operation.

Dependencies/integration points: MinIO client `GetLifecycle`, colorjson, lifecycle configuration types.

Risks: console and JSON outputs have different envelopes. Empty lifecycle configuration is treated as an error rather than exporting an empty config.

Test signals: no direct tests; should cover empty config, JSON envelope, and updatedAt propagation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-rule-export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-rule-import.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-rule-import.go

Purpose: implements `mc ilm rule import`, replacing bucket lifecycle configuration from JSON read on stdin.

Important APIs/types/functions: `ilmImportCmd`, `ilmImportMessage`, `readILMConfig`, `checkILMImportSyntax`, and `mainILMImport`.

Control flow: validates one target, reads a `lifecycle.Configuration` from `os.Stdin` with colorjson decoder, rejects configs with zero rules to avoid accidental lifecycle deletion, writes via `SetLifecycle`, and prints success.

State and persistence: replaces server-side bucket lifecycle configuration.

Dependencies/integration points: MinIO lifecycle client, stdin, colorjson, console message formatting.

Risks: full-replacement operation can remove existing rules not present in input. No explicit validation beyond JSON decode and non-empty rule list is performed here; server validation handles invalid lifecycle data.

Test signals: no direct tests; should cover invalid JSON, empty rules rejection, and successful SetLifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-rule-import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-rule-list.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-rule-list.go

Purpose: implements `mc ilm rule list`/`ls`, displaying lifecycle rules in JSON or human tables.

Important APIs/types/functions: `ilmListFlags`, `ilmLsCmd`, `ilmListMessage`, `validateILMListFlagSet`, `checkILMListSyntax`, and `mainILMList`.

Control flow: validates one target and mutually exclusive `--expiry`/`--transition`. It fetches lifecycle config, errors on no rules, applies `ilm.LsFilter`, then either prints JSON or converts config to ILM tables and renders with `go-pretty`.

State and persistence: read-only server operation.

Dependencies/integration points: `cmd/ilm` table conversion and filters, MinIO client lifecycle API, console table libraries.

Risks: filtering mutates the fetched slice in place, which is harmless locally but important if reused later. Empty filtered tables print nothing in console mode, which may be ambiguous.

Test signals: no direct tests; helper package has filter tests. CLI tests should cover flag conflict, empty config, JSON, and table rendering.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-rule-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-rule-main.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-rule-main.go

Purpose: registers `mc ilm rule` subcommands.

Important APIs/types/functions: `ilmRuleSubcommands`, `ilmRuleCmd`, and `mainILMRule`.

Control flow: dispatches to add, edit, list, remove, export, and import. Unknown commands route through `commandNotFound`.

State and persistence: none directly.

Dependencies/integration points: child of top-level ILM namespace, fronting lifecycle rule handlers.

Risks: command registration drift can leave handlers unreachable or hidden legacy commands as the only path.

Test signals: command-tree tests should verify full subcommand set.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-rule-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-add.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-tier-add.go

Purpose: implements `mc ilm tier add`, configuring a remote tier target for MinIO ILM transition.

Important APIs/types/functions: `adminTierAddFlags`, `adminTierAddCmd`, `checkAdminTierAddSyntax`, `supportedAWSTierSC`, `fetchTierConfig`, `tierMessage`, `tierMessage.SetTierConfig`, and `mainAdminTierAdd`.

Control flow: validates `TYPE ALIAS NAME`, converts type with `madmin.NewTierType`, builds a provider-specific `madmin.TierConfig` from flags, creates an admin client, and calls `AddTier` or hidden `AddTierIgnoreInUse` when `--force` is used. Provider branches support MinIO, S3, Azure, and GCS credentials/options.

State and persistence: persists remote-tier configuration on the MinIO server. Reads GCS credential files locally.

Dependencies/integration points: madmin tier constructors, server admin APIs, console/colorjson output.

Risks: credential validation is complex, especially S3 role modes and Azure service principal fields. Tier names are uppercased before creation. Hidden force bypasses in-use checks and needs careful guard coverage.

Test signals: no direct tests; provider matrix validation and error cases should be unit tested with fake CLI contexts.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-check.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-tier-check.go

Purpose: registers visible `mc ilm tier check` as a remote-tier connectivity validation command.

Important APIs/types/functions: `ilmTierCheckCmd`, which delegates to `mainAdminTierVerify`.

Control flow: this file only declares command metadata and help. Runtime validation and server call are shared with the verify implementation.

State and persistence: read-only validation through server admin API.

Dependencies/integration points: uses `mainAdminTierVerify` from `ilm-tier-verify.go`.

Risks: shares output operation name with `ctx.Command.Name`, so messages distinguish `check` from hidden `verify`.

Test signals: command wiring test should verify `check` is visible and calls the verify handler.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-edit.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-tier-edit.go

Purpose: implements hidden `mc ilm tier edit` and shared handler for visible `update`, updating remote-tier credentials.

Important APIs/types/functions: `adminTierEditFlags`, `adminTierEditCmd`, `checkAdminTierEditSyntax`, and `mainAdminTierEdit`.

Control flow: validates `ALIAS NAME`, collects credential flags into `madmin.TierCreds`, chooses one credential mode, reads GCS credential file if supplied, calls `EditTier`, and prints a tier message.

State and persistence: mutates server-side remote-tier credential configuration. Reads local credential file for GCS update.

Dependencies/integration points: `ilm-tier-update.go` reuses this handler and flag set. Uses madmin `EditTier`.

Risks: Azure service-principal branch accepts partial SP fields and relies on server validation. Static S3 credentials require both access and secret keys; `use-aws-role` overrides other modes.

Test signals: no direct tests; should cover each credential branch, insufficient credentials, and update alias wiring.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-edit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-info.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-tier-info.go

Purpose: implements `mc ilm tier info`, showing usage statistics for configured tiers.

Important APIs/types/functions: `adminTierInfoCmd`, `checkAdminTierInfoSyntax`, `tierInfos`, `tierInfoType`, `mainAdminTierInfo`, and `tierInfoMessage`.

Control flow: validates alias and optional tier name, disallowing a tier name with JSON output. It fetches `TierStats`, builds JSON status if requested, otherwise filters table rows by tier. If a named tier has no stats, it calls `ListTiers` to verify the tier exists and shows an empty stats row.

State and persistence: read-only server admin queries.

Dependencies/integration points: madmin `TierStats` and `ListTiers`, lipgloss table renderer, humanized bytes.

Risks: if `TierStats` fails, non-JSON path still proceeds to use `tInfos`, which can hide errors or print empty data; JSON path reports the error. Named tier matching is exact and case-sensitive.

Test signals: no direct tests; cover error path, empty tiers, named tier with no stats, and JSON restriction.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-list.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-tier-list.go

Purpose: implements `mc ilm tier list`/`ls`, displaying configured remote tier targets.

Important APIs/types/functions: `adminTierListCmd`, `checkAdminTierListSyntax`, `storageClass`, `tierListMessage`, `mainAdminTierList`, and `tierTable`.

Control flow: validates one alias, fetches tiers with `ListTiers`, prints an informational message when none exist, emits JSON when requested, or sorts tiers by name and renders a lipgloss table with endpoint, bucket, prefix, region, and storage class.

State and persistence: read-only server admin query.

Dependencies/integration points: madmin tier config types and UI table library.

Risks: JSON path preserves server order while console path sorts by name. Empty tier list is not emitted as JSON because the early return precedes `globalJSON`.

Test signals: no direct tests; should cover empty list, JSON output, sorting, and storage-class extraction per provider.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-main.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-tier-main.go

Purpose: registers the `mc ilm tier` namespace.

Important APIs/types/functions: `ilmTierSubcommands`, `ilmTierCmd`, and `mainILMTier`.

Control flow: dispatches tier info, list, add, edit, update, verify, check, and remove. Unknown commands route to `commandNotFound`.

State and persistence: no direct state changes.

Dependencies/integration points: child of top-level ILM command and registration point for remote tier management.

Risks: both hidden and visible aliases are present (`edit`/`update`, `verify`/`check`), so changes should preserve intended compatibility.

Test signals: command-tree registration tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-remove.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-tier-remove.go

Purpose: implements `mc ilm tier remove`/`rm`, deleting a remote tier target.

Important APIs/types/functions: `adminTierRmFlags`, `adminTierRmCmd`, and `mainAdminTierRm`.

Control flow: validates exactly `ALIAS NAME`, rejects empty tier names, requires hidden `--dangerous` when hidden `--force` is set, creates admin client, and calls `RemoveTierV2` with `madmin.RemoveTierOpts{Force}`.

State and persistence: removes or disconnects server-side tier configuration. Force can be irreversible for a tier with data.

Dependencies/integration points: madmin tier remove API and shared `tierMessage` output.

Risks: hidden force/dangerous path is intentionally high risk. Non-force removes only empty tiers, relying on server enforcement.

Test signals: no direct tests; cover arity, force/dangerous coupling, and request option propagation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-update.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-tier-update.go

Purpose: exposes visible `mc ilm tier update` as the credential update command.

Important APIs/types/functions: `ilmTierUpdateCmd`, reusing `adminTierEditFlags` and `mainAdminTierEdit`.

Control flow: command metadata and help only; runtime logic is fully shared with hidden `edit`.

State and persistence: mutates server-side tier credentials via shared handler.

Dependencies/integration points: depends on `ilm-tier-edit.go`.

Risks: changes to edit flags/handler immediately affect update. Help should remain aligned with the shared implementation.

Test signals: command registration test should verify update is visible and delegates to edit handler.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-verify.go -->
# Research: sources/object-store/minio-mc/cmd/ilm-tier-verify.go

Purpose: implements hidden `mc ilm tier verify`, shared with visible `check`, to validate remote-tier configuration/connectivity.

Important APIs/types/functions: `adminTierVerifyCmd` and `mainAdminTierVerify`.

Control flow: validates exactly alias and tier name, creates admin client, calls `VerifyTier`, and prints a tier message using the invoked command name.

State and persistence: read-only validation, though server may perform remote connectivity checks.

Dependencies/integration points: madmin `VerifyTier`; visible `check` command delegates here.

Risks: connectivity checks may be slow or depend on external remote storage availability. Empty tier names are rejected locally.

Test signals: no direct tests; cover arity, empty tier, and message op for verify/check aliases.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm-tier-verify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm/options.go -->
# Research: sources/object-store/minio-mc/cmd/ilm/options.go

Purpose: converts ILM CLI options into MinIO lifecycle rules and applies partial edits to existing rules.

Important APIs/types/functions: `RemoveILMRule`, `LifecycleOptions`, `LifecycleOptions.Filter`, `LifecycleOptions.ToILMRule`, pointer helpers, `GetLifecycleOptions`, and `ApplyRuleFields`.

Control flow: `GetLifecycleOptions` reads CLI flags, supports deprecated and current flag names, infers prefix from target path when `--prefix` is absent, parses sizes with humanize, uppercases tier names, enforces transition-day requirements when tiers are set, and limits expiry action flags. `ToILMRule` builds a lifecycle rule and validates it via parse helpers. `ApplyRuleFields` applies only provided fields, resetting mutually exclusive date/day/delete-marker fields where appropriate.

State and persistence: pure in-memory transformation; callers persist with `SetLifecycle`.

Dependencies/integration points: MinIO lifecycle structs, `probe`, `xid`, `humanize`, and `cli.Context`.

Risks: edit semantics are partial and nuanced. Prefix inference from target path is deprecated but still active. Some validation is split between option parsing and `parse.go`, so changes can introduce inconsistent acceptance.

Test signals: `options_test.go` covers filter construction. More tests are needed for `GetLifecycleOptions`, `ToILMRule`, and `ApplyRuleFields`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm/options_test.go -->
# Research: sources/object-store/minio-mc/cmd/ilm/options_test.go

Purpose: unit tests for lifecycle filter construction from `LifecycleOptions`.

Important APIs/types/functions: `TestOptionFilter` and local `filterEq` comparator.

Control flow: builds expected filters for empty, prefix, tag, size-lt, size-gt, and combined predicate cases. Each test calls `opts.Filter()` and compares scalar fields and `And.Tags`.

State and persistence: no persistence; pure unit tests.

Dependencies/integration points: `testing`, `humanize`, and MinIO lifecycle types.

Risks: tests cover filter construction only, not validation or full lifecycle rule generation. Comparator is local and must evolve if lifecycle filter fields expand.

Test signals: positive test signal for the single-predicate versus `And` behavior in `Filter`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm/options_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm/parse.go -->
# Research: sources/object-store/minio-mc/cmd/ilm/parse.go

Purpose: parses and validates lifecycle rule fields for ILM commands.

Important APIs/types/functions: `extractILMTags`, validation helpers for transition/expiration/current date/noncurrent rules, `validateILMRule`, `parseTransitionDate`, `parseTransitionDays`, `parseTransition`, `parseExpiryDate`, `parseExpiryDays`, and `parseExpiry`.

Control flow: tag strings split on `&` and first `=`. Validation requires at least one action, enforces single expiration/transition mode, checks dates are not in the past, ensures transition before expiration, enforces storage class presence, and validates noncurrent days/storage class. Parse helpers convert `YYYY-MM-DD` dates and integer day strings into lifecycle types.

State and persistence: pure in-memory parsing/validation.

Dependencies/integration points: `lifecycle` types and `probe` errors. Called from `LifecycleOptions.ToILMRule` and `ApplyRuleFields`.

Risks: tag parsing is permissive and allows key without value. Date validation uses local current date truncated to day, so tests involving dates can be time-sensitive. STANDARD_IA minimum transition day rule is hard-coded.

Test signals: no direct parse tests; add table tests for invalid combinations and date/day parsing.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm/table.go -->
# Research: sources/object-store/minio-mc/cmd/ilm/table.go

Purpose: defines table abstractions and row types for rendering lifecycle rules.

Important APIs/types/functions: `Table`, `LsFilter`, `LsFilter.Apply`, current/noncurrent expiration and transition table/row types, and their `Len`, `Title`, `Rows`, and `ColumnHeaders` methods.

Control flow: `LsFilter.Apply` filters lifecycle rules in place based on expiry or transition actions. Table row builders normalize empty prefix/tags to `-` and return `go-pretty` rows with stable headers.

State and persistence: pure display transformation; no persistence.

Dependencies/integration points: used by `ilm-rule-list.go` and `utils.go` `ToTables`.

Risks: `Apply` mutates the input slice contents and length, so callers should not expect original ordering plus excluded rules afterward. Table headers are user-facing and JSON-independent.

Test signals: `options_test.go` does not cover this; useful tests would verify filter behavior and row output for empty fields.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm/table.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm/utils.go -->
# Research: sources/object-store/minio-mc/cmd/ilm/utils.go

Purpose: extracts display fields from lifecycle rules and converts a lifecycle configuration into renderable ILM tables.

Important APIs/types/functions: `getPrefix`, `getTags`, `getExpirationDays`, `getTransitionDays`, and `ToTables`.

Control flow: prefix lookup handles deprecated top-level `Rule.Prefix`, filter prefix, then `And.Prefix`. Tag formatting handles single tag or `And.Tags` joined with `&`. Day helpers convert absolute dates to days from current time. `ToTables` walks rules and appends rows to current expiration, noncurrent expiration, current transition, and noncurrent transition tables, returning only non-empty tables.

State and persistence: pure in-memory display conversion.

Dependencies/integration points: lifecycle types and table row structs from `table.go`.

Risks: absolute-date-to-days output changes with time. `DeleteAll` expiration is not surfaced in the current table fields. Deprecated prefix support is important for old configs.

Test signals: `utils_test.go` covers tag formatting; more coverage needed for prefix precedence and table inclusion.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm/utils_test.go -->
# Research: sources/object-store/minio-mc/cmd/ilm/utils_test.go

Purpose: unit tests for lifecycle tag display formatting.

Important APIs/types/functions: `TestILMTags`.

Control flow: constructs one rule with a single `RuleFilter.Tag` and another with multiple `RuleFilter.And.Tags`; asserts `getTags` returns `key=value` or `key=value&...` strings.

State and persistence: no persistence.

Dependencies/integration points: standard testing and MinIO lifecycle types.

Risks: only tag formatting is covered. It does not test empty tags, key-only tags, ordering assumptions beyond the configured slice order, or escaping.

Test signals: confirms stable tag string formatting used by ILM list tables.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ilm/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/legalhold-clear.go -->
# Research: sources/object-store/minio-mc/cmd/legalhold-clear.go

Purpose: implements `mc legalhold clear`, disabling legal hold for one object, a version, or recursively listed objects/versions.

Important APIs/types/functions: `lhClearFlags`, `legalHoldClearCmd`, and `mainLegalHoldClear`.

Control flow: sets console colors, parses shared legalhold args, defaults `--versions` without `--rewind` to current time, verifies bucket locking is enabled, and calls `setLegalHold` with `minio.LegalHoldDisabled`.

State and persistence: mutates object legal hold status server-side.

Dependencies/integration points: shared parser and setter from legalhold set file, bucket-lock check from legalhold main, MinIO object lock APIs.

Risks: recursive clears are destructive for retention workflows. The command depends on correct bucket-lock detection before mutation.

Test signals: no direct tests; should cover version flag conflicts, bucket-lock disabled, and recursive clear behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/legalhold-clear.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/legalhold-info.go -->
# Research: sources/object-store/minio-mc/cmd/legalhold-info.go

Purpose: implements `mc legalhold info`, showing legal hold status for objects and versions.

Important APIs/types/functions: `lhInfoFlags`, `legalHoldInfoCmd`, `legalHoldInfoMessage`, `showLegalHoldInfo`, and `mainLegalHoldInfo`.

Control flow: parses args and bucket-lock status, then either fetches legal hold directly for a single object or lists matching objects/versions and fetches hold status for each. Console output prints status, optional version ID, and key. JSON output for recursive mode suppresses per-object prints in current code path.

State and persistence: read-only object-lock query.

Dependencies/integration points: MinIO client `GetObjectLegalHold`, list APIs, alias expansion, `parseRewindFlag`, and common legalhold colors.

Risks: recursive error handling can continue after per-object failures, returning only listing errors as exit status. JSON behavior in recursive path appears incomplete because successful recursive items are only printed when not JSON.

Test signals: no direct tests; cover single-object JSON, recursive console, not-found object/version, and bucket-lock disabled.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/legalhold-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/legalhold-main.go -->
# Research: sources/object-store/minio-mc/cmd/legalhold-main.go

Purpose: registers legalhold commands and provides shared object-lock status helpers and success message type.

Important APIs/types/functions: `legalHoldSubcommands`, `legalHoldCmd`, `legalHoldCmdMessage`, `isBucketLockEnabled`, `getBucketLockStatus`, and `mainLegalHold`.

Control flow: command dispatches set, clear, and info. `getBucketLockStatus` creates a client, strips object path to bucket root for S3 clients, calls `GetObjectLockConfig`, and maps not-configured/not-implemented responses to sentinel errors. `isBucketLockEnabled` converts those sentinel errors to false.

State and persistence: read-only bucket object-lock config lookup; message type is output-only.

Dependencies/integration points: S3 client implementation, MinIO error response conversion, HTTP status codes, shared console output.

Risks: non-S3 targets are treated as object-lock unsupported. Object path stripping assumes URL/object mapping from `S3Client.url2BucketAndObject`.

Test signals: no direct tests; should cover no object-lock config, unsupported filesystem target, S3 bucket URL versus object URL, and enabled status.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/legalhold-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/legalhold-set.go -->
# Research: sources/object-store/minio-mc/cmd/legalhold-set.go

Purpose: implements `mc legalhold set` and shared logic for applying legal hold status.

Important APIs/types/functions: `lhSetFlags`, `legalHoldSetCmd`, `setLegalHold`, `parseLegalHoldArgs`, and `mainLegalHoldSet`.

Control flow: `parseLegalHoldArgs` validates one non-empty target, disallows `--version-id` with recursive/version/rewind flags, and parses rewind. `mainLegalHoldSet` checks bucket locking and calls `setLegalHold` with enabled status. `setLegalHold` either calls `PutObjectLegalHold` directly or lists objects/versions and applies status to each listed object, printing per-object messages in console mode.

State and persistence: mutates object legal hold status server-side.

Dependencies/integration points: MinIO object-lock API, list behavior, alias expansion, `parseRewindFlag` from `ls-main.go`, and shared messages from legalhold main.

Risks: recursive set can touch many objects and versions. JSON recursive success output is suppressed by `if !globalJSON`, so scripts may not receive per-object success entries.

Test signals: no direct tests; should cover parser conflicts, empty target, direct set, recursive set, no objects found, and JSON behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/legalhold-set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/license-info.go -->
# Research: sources/object-store/minio-mc/cmd/license-info.go

Purpose: implements `mc license info`, displaying SUBNET license or AGPL status for a cluster alias.

Important APIs/types/functions: `licenseInfoCmd`, `licInfoMessage`, `licInfo`, color helper functions, `getLicInfoStr`, `getAGPLMessage`, `initLicInfoColors`, `mainLicenseInfo`, `getLicInfoMsg`, and `licErrMsg`.

Control flow: validates one alias, initializes SUBNET connectivity in check mode, reads stored API key/license with `getSubnetCreds`, parses license if present, reports registered-without-license if only API key exists, or displays AGPL message if unregistered. Console output uses a styled table for license fields.

State and persistence: read-only local SUBNET credential/license config and possible connectivity initialization.

Dependencies/integration points: SUBNET helpers, license parser, bubbles/lipgloss table UI, colorjson.

Risks: `getLicInfoStr` assumes `IssuedAt` and `ExpiresAt` pointers are non-nil. Invalid stored license returns an error message instead of falling back.

Test signals: no direct tests; cover no creds, API key only, valid license, invalid license, and JSON output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/license-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/license-register.go -->
# Research: sources/object-store/minio-mc/cmd/license-register.go

Purpose: implements `mc license register`, registering a MinIO cluster with SUBNET online or generating offline registration URLs.

Important APIs/types/functions: `licenseRegisterFlags`, `licenseRegisterCmd`, `licRegisterMessage`, `ClusterRegistrationReq`, `ClusterRegistrationInfo`, `ClusterInfo`, `SubnetLoginReq`, `SubnetMFAReq`, `isPlay`, `validateNotPlay`, `mainLicenseRegister`, and `getAdminInfo`.

Control flow: validates one target, rejects the public play cluster, optionally reads a license file and saves it, otherwise initializes SUBNET connectivity. It derives cluster name, fetches server info, builds registration info, attempts online registration if not airgapped, marks action registered or updated, and falls back to offline token URL on failure or airgap.

State and persistence: may store license/API key locally through SUBNET helpers and registers/updates cluster state in SUBNET. Reads local license files and server info.

Dependencies/integration points: DNS lookup for play detection, madmin `ServerInfo`, SUBNET registration/token helpers, local config helpers.

Risks: play detection relies on DNS unless airgapped. Online failure falls back to offline URL instead of hard failing. Registration sends cluster inventory/capacity metadata.

Test signals: no direct tests; cover play rejection, license-file path, airgap mode, already registered update, and offline fallback.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/license-register.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/license-unregister.go -->
# Research: sources/object-store/minio-mc/cmd/license-unregister.go

Purpose: implements hidden `mc license unregister`, unregistering a cluster from SUBNET and removing local auth config.

Important APIs/types/functions: `licenseUnregisterCmd`, `licUnregisterMessage`, `checkLicenseUnregisterSyntax`, and `mainLicenseUnregister`.

Control flow: validates one target, initializes SUBNET connectivity, obtains or validates API key, calls SUBNET unregister with deployment ID unless airgapped, removes local SUBNET auth config, and prints success.

State and persistence: mutates SUBNET registration state online and deletes local SUBNET auth/config for the alias.

Dependencies/integration points: SUBNET helpers, `getAdminInfo`, local config removal.

Risks: hidden but destructive for support registration. In airgapped mode it only removes local config, not remote SUBNET state.

Test signals: no direct tests; cover registered/unregistered aliases, airgap, API key flag, and local config removal.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/license-unregister.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/license-update.go -->
# Research: sources/object-store/minio-mc/cmd/license-update.go

Purpose: implements `mc license update`, either saving a provided license file or renewing from SUBNET.

Important APIs/types/functions: `licenseUpdateCmd`, `licUpdateMessage`, `mainLicenseUpdate`, `performLicenseRenew`, and `performLicenseUpdate`.

Control flow: accepts alias plus optional license-file path. With a file, it reads the license and calls `validateAndSaveLic`. Without a file, it loads stored SUBNET API key, fails if not registered, posts to the license-renew endpoint with API-key auth and deployment ID, then extracts and saves returned credentials.

State and persistence: updates local license/SUBNET credentials and may call SUBNET to renew license.

Dependencies/integration points: local file IO, SUBNET HTTP helpers, alias config, deployment ID header helper.

Risks: renewal requires existing API key and remote SUBNET availability. File update trusts `validateAndSaveLic` for license validation and storage.

Test signals: no direct tests; cover arg count, file read errors, unregistered renew, successful renew credential extraction.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/license-update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/license.go -->
# Research: sources/object-store/minio-mc/cmd/license.go

Purpose: registers the `mc license` command namespace.

Important APIs/types/functions: `licenseSubcommands`, `licenseCmd`, and `mainlicense`.

Control flow: dispatches register, info, update, and hidden unregister. Unknown subcommands go through `commandNotFound`.

State and persistence: none directly; subcommands manage SUBNET/local license state.

Dependencies/integration points: top-level CLI integration for license support commands.

Risks: hidden unregister remains part of command tree. Function name `mainlicense` is non-standard casing but local only.

Test signals: command-tree tests should verify visible and hidden command registration.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/license.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ls-main.go -->
# Research: sources/object-store/minio-mc/cmd/ls-main.go

Purpose: implements top-level `mc ls` command argument parsing and dispatch.

Important APIs/types/functions: `lsFlags`, `lsCmd`, `rewindSupportedFormat`, `parseRewindFlag`, `checkListSyntax`, and `mainList`.

Control flow: `parseRewindFlag` parses fixed date formats or positive durations into a reference time. `checkListSyntax` defaults to `.`, rejects blank args, parses recursive/incomplete/version/summary/storage-class/zip options, and rejects zip with versions/rewind. `mainList` configures colors, initializes clients for each target, stats non-slash targets to append a separator for directories, and calls `doList`.

State and persistence: read-only listing. No persistence.

Dependencies/integration points: shared client abstraction, duration parser, global context, and `doList` from `ls.go`. `parseRewindFlag` is reused by legalhold commands.

Risks: local timezone affects rewind date interpretation. Zip listing is limited to latest version. Directory stat before listing adds extra remote/local calls.

Test signals: no direct tests here; useful tests cover rewind formats, invalid negative duration, zip conflicts, default target, and directory separator adjustment.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ls-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ls.go -->
# Research: sources/object-store/minio-mc/cmd/ls.go

Purpose: contains listing output models, version grouping, sorting, summary, and core listing loop for `mc ls`.

Important APIs/types/functions: `contentMessage`, `getOSDependantKey`, `getKey`, `generateContentMessages`, `sortObjectVersions`, `summaryMessage`, `printObjectVersions`, `doListOptions`, and `doList`.

Control flow: `doList` iterates `clnt.List` with recursive, incomplete, rewind, versions, delete markers, and zip options. It filters by storage class, groups consecutive entries by path, prints one or all versions, accumulates summary totals, and returns an exit status if listing errors occurred. `generateContentMessages` normalizes keys relative to the listed prefix, strips ETag quotes, marks folders/files, and sets version ordinals.

State and persistence: read-only listing; only console/JSON output.

Dependencies/integration points: client abstraction, `ClientContent`, `ListOptions`, `printMsg`, humanize, colorjson, console colors from `ls-main.go`.

Risks: version grouping assumes list output is ordered by path. Summary totals count versions/delete markers according to list output, not necessarily unique logical objects. `getOSDependantKey` currently uses `/` regardless of OS despite its name.

Test signals: `ls_test.go` is effectively empty. Tests should cover version sorting, prefix trimming, storage-class filtering, summary counts, and error continuation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ls_test.go -->
# Research: sources/object-store/minio-mc/cmd/ls_test.go

Purpose: placeholder test file for the `cmd` package.

Important APIs/types/functions: none beyond package declaration and license header.

Control flow: no executable tests are defined.

State and persistence: none.

Dependencies/integration points: establishes no test coverage for `ls` behavior despite adjacent listing code.

Risks: presence of the file may suggest `ls` has tests when it does not. Listing behavior has enough formatting and version-ordering logic to warrant real tests.

Test signals: negative signal: no tests. Candidate tests include `sortObjectVersions`, `generateContentMessages`, `doList` error handling, and `parseRewindFlag` in `ls-main.go`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ls_test.go -->
