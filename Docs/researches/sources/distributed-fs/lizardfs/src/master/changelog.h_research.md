# sources/distributed-fs/lizardfs/src/master/changelog.h

Purpose: public interface for changelog initialization, writing, rotation, and flush policy.

Important APIs/types/functions: `kMaxLogLineSize`, `changelog_init`, `changelog_get_back_logs_config_value`, `changelog_rotate`, `changelog`, `changelog_flush`, `changelog_disable_flush`, `changelog_enable_flush`.

Control flow: callers initialize with a base filename and accepted `BACK_LOGS` range, then append formatted metadata operation strings by version.

State and persistence: API controls persistent changelog files through the implementation.

Dependencies and integration: included by master metadata mutation and restoration paths.

Risks: header documents entry format but does not enforce max line length at the interface.

Test signals: no direct tests in this subset.
