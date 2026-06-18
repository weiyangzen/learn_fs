# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/btbcm.h

## Purpose

`btbcm.h` is the public header for the Broadcom Bluetooth helper library. It defines vendor command parameter layouts and exposes helper APIs to transport drivers while providing no-op or unsupported inline stubs when `CONFIG_BT_BCM` is disabled.

## Important APIs, Types, And Functions

The header defines Broadcom UART clock constants `BCM_UART_CLOCK_48MHZ` and `BCM_UART_CLOCK_24MHZ`. Packed command parameter structs include `bcm_update_uart_baud_rate`, `bcm_write_uart_clock_setting`, `bcm_set_sleep_mode`, `bcm_set_pcm_int_params`, and `bcm_set_pcm_format_params`. These model vendor command payloads used by Broadcom transports for UART speed/clock, sleep behavior, and PCM/I2S audio interface setup.

When `IS_ENABLED(CONFIG_BT_BCM)` is true, the header declares `btbcm_check_bdaddr`, `btbcm_set_bdaddr`, `btbcm_patchram`, PCM parameter read/write helpers, `btbcm_setup_patchram`, `btbcm_setup_apple`, `btbcm_initialize`, and `btbcm_finalize`. When disabled, inline stubs return `-EOPNOTSUPP` for operations that require the helper module and zero for setup/finalize routines that callers may treat as optional.

## Control Flow

There is no runtime logic beyond inline stubs. The header controls compile-time call behavior: transports can include it unconditionally, and the compiler either binds to exported helper symbols or inlines fallback behavior depending on Kconfig. This reduces preprocessor conditionals in transport drivers.

## State And Persistence

The structs describe transient HCI vendor command payloads. No persistent state is defined here. Callers store any runtime state, such as firmware load completion, HCI quirks, or UART baud settings.

## Dependencies And Integration Points

The declarations expect Bluetooth HCI types such as `struct hci_dev`, `bdaddr_t`, and `struct firmware` to be visible through including contexts. The header integrates Kconfig with source-level availability through `IS_ENABLED(CONFIG_BT_BCM)`. It is consumed by Broadcom-capable transports and implemented by `btbcm.c`.

## Risks

The packed layout of vendor command structs is an ABI contract with Broadcom firmware; padding or field order changes would break commands. Stub return values matter: setup stubs returning zero can allow generic transport initialization to continue without Broadcom-specific setup, while direct helper calls return `-EOPNOTSUPP`. Changes should preserve this distinction. Long prototype lines should remain synchronized with exported implementations in `btbcm.c`.

## Test Signals

Build tests should cover both `CONFIG_BT_BCM=y/m` and disabled configurations for transports that include this header. Runtime tests with `BT_BCM` enabled should exercise PatchRAM setup, BDADDR checks, PCM parameter commands, and Apple setup. Disabled-helper builds should confirm transports either avoid unsupported direct calls or handle `-EOPNOTSUPP`.
