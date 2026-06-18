# sources/distributed-fs/ceph-client/drivers/bluetooth/btrtl.h

## Purpose

`btrtl.h` is the public interface and shared wire-format header for Realtek Bluetooth support. It provides firmware/config structure definitions, Realtek logging wrappers, Realtek private HCI data, flag helpers, and exported function declarations or disabled stubs depending on `CONFIG_BT_RTL`.

## Important APIs, Types, and Functions

- `RTL_FRAG_LEN` defines the 252-byte payload fragment size used by Realtek firmware download commands.
- Packed structures such as `rtl_download_cmd`, `rtl_download_response`, `rtl_rom_version_evt`, `rtl_epatch_header`, `rtl_epatch_header_v2`, `rtl_vendor_config`, and subsection headers describe controller command responses and firmware/config file formats.
- `struct rtl_subsection` and `struct rtl_iovec` support EPATCH v2 parsing in `btrtl.c`.
- `struct btrealtek_data` is the HCI private area used by transports that allocate Realtek private data. It stores a bitmap of Realtek flags and devcoredump metadata.
- Flag helpers `btrealtek_set_flag()`, `btrealtek_get_flag()`, and `btrealtek_test_flag()` wrap `hci_get_priv()` access.
- Public helpers include `btrtl_initialize()`, `btrtl_free()`, `btrtl_download_firmware()`, `btrtl_set_quirks()`, `btrtl_setup_realtek()`, `btrtl_shutdown_realtek()`, `btrtl_get_uart_settings()`, and `btrtl_set_driver_name()`.

## Control Flow

There is no runtime control flow beyond macros and inline stubs. Compile-time flow is important: when `CONFIG_BT_RTL` is enabled, transports link against the real helper functions. When disabled, stubs return `-EOPNOTSUPP` or `-ENOENT` and do nothing for cleanup, quirks, or driver naming.

## State and Persistence

The header defines state layout but does not allocate or persist anything itself. `struct btrealtek_data` is stored as HCI private data by transport drivers, and `struct btrtl_device_info` remains opaque to callers.

## Dependencies and Integration Points

The header assumes Bluetooth HCI core types (`struct hci_dev`, private data, quirks), kernel list/bitmap support, and packed little-endian kernel integer types. It is consumed by `btrtl.c`, `btusb.c`, and UART drivers needing Realtek firmware and config support.

## Risks

The flag macros assume the HCI private area is a valid `struct btrealtek_data`; using them on an HCI device allocated without the Realtek private size will corrupt memory or crash. Packed firmware structure definitions are ABI-like, so field changes can break firmware parsing. Stub behavior is also externally visible: callers must treat `-EOPNOTSUPP` as feature absence, not a fatal transport failure unless Realtek support is mandatory.

## Test Signals

Build coverage should include both `CONFIG_BT_RTL=y/m` and disabled configurations. Runtime tests should confirm Realtek transports allocate enough private data before using flag helpers, and disabled builds should still compile callers that include the header.
