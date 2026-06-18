# sources/distributed-fs/ceph-client/security/apparmor/procattr.c

Purpose: implements AppArmor's `/proc/<pid>/attr/` label display and `change_hat` write parsing.

Important APIs, types, and functions: public functions are `aa_getprocattr()` and `aa_setprocattr_changehat()`. Internal `split_token_from_name()` parses the `<hex-token>^<hat-name>` procattr format.

Control flow: `aa_getprocattr()` gets the current AppArmor namespace, checks whether the target label namespace is visible, measures formatted label length with `aa_label_snxprint()`, allocates a buffer, prints label mode/name with subnamespace visibility and hidden-unconfined flags, appends an optional newline, and returns the length. `aa_setprocattr_changehat()` parses the token, builds a vector of up to 16 NUL-separated hat names, then calls `aa_change_hat()`.

State and persistence: reads current namespace/label state and allocates a returned string for procfs callers. It does not directly mutate policy; mutation is delegated to domain transition code through `aa_change_hat()`.

Dependencies and integration: integrates with procattr LSM hooks, AppArmor namespace visibility, label rendering, domain transitions, and AppArmor debug/error logging.

Risks and test signals: namespace visibility failures must not leak label names. The parser must reject malformed tokens, empty token/name combinations, and overlong hat vectors. Test signals include procattr reads from same/sub/hidden namespaces and writes for single hat, multi-hat, restore-token, malformed delimiter, and zero-token cases.
