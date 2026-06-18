# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/btbcm.c

## Purpose

`btbcm.c` is a shared Broadcom Bluetooth helper library used by transport drivers. It validates or programs controller addresses, sends Broadcom vendor commands, loads PatchRAM firmware, reads controller identity and feature data, chooses firmware filenames, and applies Broadcom-specific HCI quirks.

## Important APIs, Types, And Functions

Exported functions include `btbcm_check_bdaddr`, `btbcm_set_bdaddr`, `btbcm_read_pcm_int_params`, `btbcm_write_pcm_int_params`, `btbcm_patchram`, `btbcm_initialize`, `btbcm_finalize`, `btbcm_setup_patchram`, and `btbcm_setup_apple`. Helper functions read local name, local version, verbose config, controller features, and USB product info using synchronous HCI commands. `bcm_uart_subver_table` and `bcm_usb_subver_table` map `lmp_subver` values to firmware hardware names. `btbcm_get_board_name` derives a firmware board suffix from the device-tree root compatible string when OF is enabled.

## Control Flow

`btbcm_setup_patchram` calls `btbcm_initialize`, then `btbcm_finalize`. Initialization resets the controller, reads local version, optionally reads verbose info, features, and name, maps subversion to a hardware name, logs version/build identity, and, if firmware has not already been loaded, builds a prioritized list of up to four firmware names. USB devices add a `-vid-pid` postfix read from vendor command `0xfc5a`; device-tree board names add an additional suffix. The first successfully requested `.hcd` file is sent through `btbcm_patchram`, which starts minidrv mode with command `0xfc2e`, waits, iterates embedded HCI command records from the firmware, sends each synchronously, and waits after launch.

Finalization reruns initialization if firmware was loaded, checks for default/invalid Broadcom addresses, and sets `HCI_QUIRK_STRICT_DUPLICATE_FILTER`. Address checking compares the controller BDADDR against known factory placeholder addresses and tries to set a real address from EFI variable `BDADDR` before marking `HCI_QUIRK_INVALID_BDADDR`. The Apple setup path reads and logs identity information without PatchRAM loading and also sets strict duplicate filtering.

## State And Persistence

The file keeps little module-global state beyond static tables. State is mostly in the controller and in caller-provided `fw_load_done`. Firmware loading changes controller RAM state and usually requires reinitialization. EFI BDADDR is persistent platform state; the driver reads it and writes it into the controller if needed. HCI quirks persist in `struct hci_dev` for the device lifetime.

## Dependencies And Integration Points

The helper depends on HCI core synchronous command APIs, firmware loader, EFI runtime services, DMI, device tree, unaligned access helpers, and Bluetooth address utilities. It exports symbols for USB, UART, SDIO, and platform Broadcom transports selected through `CONFIG_BT_BCM`. DMI entries mark specific Apple systems with broken Read LE Min/Max Tx Power behavior.

## Risks

PatchRAM parsing trusts the firmware as a stream of HCI command headers and payloads but validates remaining size before each command. Filename selection is compatibility-critical; changing order can alter which firmware file wins on systems with board-specific blobs. `btbcm_initialize` returns success even when no firmware is found after logging attempted names, which lets transports continue with ROM firmware; callers must understand that behavior. Address placeholder matching is conservative and should be updated carefully because marking invalid addresses changes user-visible Bluetooth identity behavior.

## Test Signals

Signals include HCI command success for reset/version/vendor reads, expected firmware filename attempts, PatchRAM command progress, reinitialization after patch, BDADDR validation, EFI BDADDR application, and quirks set for duplicate filtering, invalid BDADDR, and Apple DMI transmit-power behavior. Test USB and UART buses because firmware naming tables and USB product postfix handling differ.
