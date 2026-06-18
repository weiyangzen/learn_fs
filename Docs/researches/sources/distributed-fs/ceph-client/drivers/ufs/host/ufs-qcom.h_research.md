# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-qcom.h

## Purpose
`ufs-qcom.h` is the private interface and register map for the Qualcomm UFS host variant. It defines vendor register offsets, bit masks, UniPro vendor attributes, controller revision helpers, reset helpers, MCQ address layout, ICE allocator constants, EOM/FOM scan coordinates, and the Qualcomm host-private data structures consumed by `ufs-qcom.c`.

## Important APIs, Types, And Macros
Important data types are `struct ufs_qcom_host`, `struct ufs_qcom_drvdata`, `struct ufs_hw_version`, `struct ufs_qcom_testbus`, and `struct ufs_eom_coord`. `ufs_qcom_host` carries the per-controller runtime state: PHY, `ufs_hba`, negotiated device parameters, lane clocks, interconnect paths, ICE handle, capabilities, device reference-clock MMIO and mask, hardware version, reset controls, device reset GPIO, host parameters, selected PHY gear, ESI state, and saved TX EQ settings.

The header exposes inline helpers `ufs_qcom_get_controller_revision()`, `ufs_qcom_assert_reset()`, `ufs_qcom_deassert_reset()`, and `ufs_qcom_get_debug_reg_offset()`, plus the non-static declaration `ufs_qcom_testbus_config()`. Register/mask definitions cover `REG_UFS_*`, debug windows, Hibern8 counters, MCQ layout, ICE configuration, clock-cycle attributes, and QCOM-specific quirks.

## Control Flow And State
The header itself has no execution path, but it shapes the driver flow. Controller revision is read from `REG_UFS_HW_VERSION` and split into major/minor/step. Reset helpers set or clear `UFS_PHY_SOFT_RESET` and perform dummy reads for posted-write ordering. Debug register offset selection depends on controller major version, mapping older 2.x controllers to a different vendor register window.

The EOM coordinate table `sw_rx_fom_eom_coords_g6` is static constant state used by the software RX FOM scan for HS-G6. ICE allocator constants describe how AES cores are shared between RX/TX traffic mixes when the controller supports vendor ICE allocator programming.

## Dependencies And Integration Points
The header depends on `<ufs/ufshcd.h>`, Qualcomm ICE, Linux reset APIs, and UFS/UniPro bit definitions supplied elsewhere. It is tightly coupled to `ufs-qcom.c`, which consumes all register offsets and structures. Its MCQ constants integrate with the core MCQ operation-register layout, and its device-quirk bits extend the shared UFS device quirk namespace.

## Risks And Edge Cases
Register definitions are silicon contracts; wrong offsets or masks can corrupt unrelated controller state. The local `ceil(freq, div)` macro is simple and could collide if included more broadly, but this private header is only intended for the QCOM driver. Static EOM coordinates encode a narrow tuning model for HS-G6 and should not be reused blindly for other controller revisions.

## Test Signals
Compile coverage should verify all masks and inline helpers against available UFS core definitions. Runtime evidence comes indirectly from QCOM probe, reset, debug dump, MCQ, ICE, EOM/FOM, and clock-scaling tests. Register dump comparisons across v2/v3+ hardware validate the version-dependent debug-offset helper.
