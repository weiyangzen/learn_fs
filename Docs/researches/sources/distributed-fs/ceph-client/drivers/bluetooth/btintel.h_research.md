# sources/distributed-fs/ceph-client/drivers/bluetooth/btintel.h

## Purpose
Defines the shared Intel Bluetooth contract between common Intel support and individual transports. It centralizes TLV identifiers, hardware/image constants, version and boot structures, DDC/SAR command payloads, per-device Intel state flags, flag helpers, and exported helper prototypes with stubs for disabled configurations.

## Important APIs, Types, And Functions
- TLV constants such as `INTEL_TLV_CNVI_TOP`, `INTEL_TLV_IMAGE_TYPE`, `INTEL_TLV_MIN_FW`, `INTEL_TLV_FW_ID`, and `INTEL_TLV_OTP_BDADDR` define the fields consumed by TLV version parsing.
- Hardware/image constants define CNVi/CNVr products, hardware variant IDs, image types `BTINTEL_IMG_BOOTLOADER`, `BTINTEL_IMG_IML`, and `BTINTEL_IMG_OP`, plus firmware ID limits.
- Packed wire structs include `struct intel_tlv`, `struct intel_version`, `struct intel_version_tlv`, `struct intel_boot_params`, `struct intel_bootup`, `struct intel_secure_send_result`, `struct intel_reset`, `struct intel_debug_features`, and `struct btintel_cp_ddc_write`.
- `struct btintel_data` is the HCI private state block used by common and PCIe code. Its bitmap is manipulated by `btintel_set_flag`, `btintel_clear_flag`, `btintel_wake_up_flag`, `btintel_test_flag`, and `btintel_wait_on_flag_timeout`.
- The prototype block exposes common Intel helpers when `CONFIG_BT_INTEL` or `CONFIG_BT_INTEL_PCIE` is enabled and otherwise supplies inline error-return stubs.

## Control Flow
This header has no runtime control flow, but it shapes setup decisions across the implementation. Version parsing fills `struct intel_version_tlv`; setup uses macros such as `INTEL_HW_PLATFORM`, `INTEL_HW_VARIANT`, `INTEL_CNVX_TOP_TYPE`, and `INTEL_CNVX_TOP_STEP` to select firmware names, feature quirks, SAR/DSBR applicability, and supported products. The state-flag macros rely on `hci_get_priv(hdev)` returning a `struct btintel_data`, so transports that use these helpers must allocate compatible private storage.

## State And Persistence
Persistent runtime state represented here is the `btintel_data.flags` bitmap and optional `acpi_reset_method` callback. The flags model firmware/boot lifecycle and device quirks: bootloader mode, active download, loaded/failed firmware, boot wait, broken command credit/shutdown behavior, legacy ROM modes, ACPI reset activity, and PCIe D0 wait. Packed structs mirror controller event/command payloads and must remain layout-stable.

## Dependencies And Integration Points
The header depends on Bluetooth core types (`struct hci_dev`, `bdaddr_t`, `struct sk_buff`), firmware and regmap declarations used by prototypes, and kernel bit/wait primitives via the including C files. It is included by `btintel.c`, Intel USB/HCI transports, and `btintel_pcie.c`; the conditional stubs let non-Intel builds compile callers while preserving link-time optionality.

## Risks And Edge Cases
Function stubs must match real prototypes; the disabled `btintel_download_firmware` stub is a compatibility-sensitive area because signature drift can break builds. Packed wire structs require endian-aware access in users. The flag helpers assume correct private-data sizing and type; using them on an HCI device not allocated with `struct btintel_data` corrupts memory. Hardware ID enums must stay synchronized with firmware naming and setup switch statements in `btintel.c` and `btintel_pcie.c`.

## Test Signals
Build coverage should include `CONFIG_BT_INTEL`, `CONFIG_BT_INTEL_PCIE`, both enabled, and both disabled caller paths. Runtime signals include correct wait-bit wakeups for `INTEL_DOWNLOADING`, `INTEL_BOOTING`, and `INTEL_WAIT_FOR_D0`; TLV version structures populated from current firmware events; and no layout regressions in packed command/event payload sizes.
