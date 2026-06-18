# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/session-protect.h

Purpose: Documents and declares the MLD session-protection interface used to request temporary firmware medium ownership around association and TDLS discovery.

Important APIs and types: Defines `struct iwl_mld_session_protect` with `end_jiffies`, `duration`, and `session_requested`; association/minimum protection constants; and declarations for notification handling, schedule, blocking start, and cancel APIs.

Control flow and integration: Consumers can choose fire-and-forget scheduling or a blocking start that waits for firmware confirmation. The header integrates with MLD VIF state and firmware MAC context command definitions.

State and persistence: The struct is embedded in VIF state and is runtime-only. `end_jiffies == 0` means inactive, so implementation uses a nonzero fallback for sessions that would otherwise calculate to zero.

Dependencies: Includes MLD core, host-command helpers, mac80211, and firmware MAC configuration definitions.

Risks: Callers must hold the expected wiphy lock in implementation paths and pass a valid link ID. Multi-link callers need care because implementation warns on more than one active link.

Test signals: Build coverage of all callers plus behavior tests for state transitions after start, reject, timeout, and cancel.
