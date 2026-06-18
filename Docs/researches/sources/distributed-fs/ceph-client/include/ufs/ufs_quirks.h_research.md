<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufs_quirks.h -->
# sources/distributed-fs/ceph-client/include/ufs/ufs_quirks.h

Purpose: defines UFS device vendor/model quirk matching and bit flags used to compensate for non-conformant or timing-sensitive UFS devices.

Important APIs and types: `STR_PRFX_EQUAL`, `UFS_ANY_VENDOR`, `UFS_ANY_MODEL`, and vendor IDs support matching. `ufs_dev_quirk` binds manufacturer/model to a quirk bitmask. Quirk bits cover DL NAC recovery, PA_TACTIVATE adjustments, regulator LPM delay, host PA_TACTIVATE/SAVECONFIGTIME/debug save config requirements, extended-feature probing, extra hibern8 time, and missing timestamp support.

Control flow: during probe or fixup, the UFS core matches device identity and sets `hba->dev_quirks`; later link startup, power-mode change, error handling, feature probing, and timestamp code checks these bits to alter behavior.

State and persistence: the header stores no state. Quirk state is runtime per device and derived from persistent manufacturer/model/spec behavior.

Dependencies and integration points: uses string matching and vendor IDs from UFS descriptors. It integrates with `ufshcd_fixup_dev_quirks()`, UniPro timing configuration, error recovery, LPM, and feature-detection paths.

Risks and test signals: risks include overly broad prefix matches, wrong vendor IDs, workaround interactions, and quirks masking real regressions. Test affected vendor devices, quirk table matching, NAC recovery timing, hibern8 entry/exit, timestamp fallback, and non-quirked devices for unchanged behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufs_quirks.h -->
