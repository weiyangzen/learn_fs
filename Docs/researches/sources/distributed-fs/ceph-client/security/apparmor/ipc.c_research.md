# sources/distributed-fs/ceph-client/security/apparmor/ipc.c

Purpose: implements AppArmor signal IPC mediation between sender and target labels.

Important functions: `map_signal_num()` converts kernel signal numbers to AppArmor DFA symbols, including realtime offsets and unknown fallback. `audit_signal_mask()` and `audit_signal_cb()` render send/receive masks, signal names, unmapped values, and peer labels. `profile_signal_perm()` performs one profile-side DFA check. `aa_may_signal()` performs bidirectional sender-write and target-read checks with `xcheck_labels()`.

Control flow: the LSM `task_kill` hook collects sender and target credentials/labels, then calls `aa_may_signal()`. For each relevant label/profile pairing, policy starts at `AA_CLASS_SIGNAL`, transitions on the mapped signal, matches the peer label, applies profile modes, and audits denied or forced-audit permissions.

State and persistence: no persistent state; all decisions derive from current labels, rulesets, and audit data. Dependencies include signal mapping tables, label matching, policy DFA, credentials, and audit.

Risks and test signals: signal aliases, realtime ranges, and signal zero existence checks are subtle. Bidirectional checks must use the correct subject credentials for send and receive. Test confined sender/receiver combinations, unconfined bypass, unknown signals, realtime signals, audit peer rendering, and policy with peer-label conditions.
