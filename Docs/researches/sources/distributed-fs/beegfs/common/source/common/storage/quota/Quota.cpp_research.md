<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/Quota.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/Quota.cpp

Purpose: Implements stream rendering for quota block-device filesystem types.

Important APIs/functions: `operator<<(std::ostream&, QuotaBlockDeviceFsType)` emits strings for `QuotaBlockDeviceFsType_EXTX`, `QuotaBlockDeviceFsType_XFS`, `QuotaBlockDeviceFsType_ZFS`, and a fallback for unknown values.

Control flow/state/persistence: The function is a switch-style formatter with no state or persistence.

Dependencies/integration: Includes `Quota.h`; output is used in logs, diagnostics, and command-line reporting.

Risks/test signals: String names are user-visible and may be parsed by scripts. Tests should verify all known enum values and unknown-value fallback formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/Quota.cpp -->
