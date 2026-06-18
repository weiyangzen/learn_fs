<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/version.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/version.h

Purpose: Defines the shared carl9170 firmware version constants expected by the driver/firmware build contract.

Important APIs/types/functions: Provides `CARL9170FW_VERSION_YEAR`, `CARL9170FW_VERSION_MONTH`, `CARL9170FW_VERSION_DAY`, and `CARL9170FW_VERSION_GIT`.

Control flow: No executable control flow; consumers include firmware parsing or compatibility checks that compare embedded firmware metadata with driver expectations.

State and persistence: Compile-time constants only. They become part of built objects but no runtime mutable state is held here.

Dependencies and integration points: Tied to `CARL9170FW_NAME` and firmware-loading logic in the carl9170 USB path. It is a shared header guarded by `__CARL9170_SHARED_VERSION_H`.

Risks and test signals: Risk is stale version metadata causing misleading firmware compatibility diagnostics. Test signals are successful firmware parse/upload and any version mismatch logging in carl9170 initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/version.h -->
