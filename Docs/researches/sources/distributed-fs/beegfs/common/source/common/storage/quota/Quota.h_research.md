<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/Quota.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/Quota.h

Purpose: Defines filesystem and inode-support enums for quota features.

Important APIs/types: `QuotaBlockDeviceFsType` enumerates unknown, ext-family, XFS, and ZFS filesystem types. `QuotaInodeSupport` records whether inode quota accounting is unknown, supported, or unsupported. The stream operator is declared here.

Control flow/state/persistence: Header-only enum definitions with no active state. Values may cross module and message boundaries.

Dependencies/integration: Includes `<ostream>`. Used by quota detection, logging, and configuration/reporting paths.

Risks/test signals: Enum numeric stability matters if serialized or stored. Tests should cover formatting and behavior when callers receive unknown filesystem or inode support status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/Quota.h -->
