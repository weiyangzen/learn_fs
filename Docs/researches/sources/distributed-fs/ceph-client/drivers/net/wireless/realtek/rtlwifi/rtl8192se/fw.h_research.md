# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/fw.h

## Purpose
This header defines RTL8192SE firmware image limits, firmware/private-header structures, firmware status states, H2C command payload structures, command ids, and firmware command register macros. It is the shared contract for `fw.c`, `phy.c`, `dm.c`, and hardware initialization.

## Important APIs, Types, And Functions
Important constants include firmware size limits, firmware header sizes, TX command header length, max transmit buffer size, and firmware DM control bits for register `0x364`/LBUS state. `struct fw_priv` describes the private DMEM header fields patched before DMEM download. `struct fw_hdr` describes the firmware file header. `struct rt_firmware` stores parsed firmware status and buffers.

H2C structures include `h2c_set_pwrmode_parm`, `h2c_joinbss_rpt_parm`, `h2c_wpa_ptk`, and `h2c_wpa_two_way_parm`. `enum h2c_cmd` selects higher-level command classes, while `enum fw_h2c_cmd` maps to firmware element ids. Macros such as `FW_CMD_IO_SET`, `FW_CMD_IO_CLR`, `FW_CMD_PARA_SET`, and query macros update firmware command map/parameter registers and cached `rtlhal` state. Public prototypes expose firmware download and H2C helpers.

## Control Flow
The header has no executable control flow, but it defines the state transitions and command ids used by firmware download and firmware-command paths. Firmware progresses through INIT, LOAD_IMEM, LOAD_EMEM, LOAD_DMEM, and READY. DM commands are encoded either as H2C packets or as firmware command-map/register updates using the macros.

## State And Persistence
`struct rt_firmware` persists in `rtlhal->pfirmware` while the driver is loaded. The command-map macros persist both in hardware registers (`LBUS_MON_ADDR`, `LBUS_ADDR_MASK`) and in cached `rtlhal->fwcmd_iomap`/`fwcmd_ioparam`. H2C sequence counters persist in `rtlhal`.

## Dependencies And Integration Points
It depends on chip register names from `reg.h` for macro writes and on firmware ABI compatibility. The RF type in `fw_priv` is patched from PHY state, so firmware header layout must match the blob. Power-save, WoWLAN, and join-report flows depend on these structure layouts matching firmware expectations exactly.

## Risks
Structure packing/alignment is critical; comments note 8-byte alignment requirements but not every struct is explicitly packed. Command IDs and DM control bits are firmware ABI values and must not be renumbered. The macros perform hardware writes and cached state updates with delays, so using them in the wrong context can block or race with other firmware command submissions. Some comments contain encoding oddities, but the field semantics are clear from usage.

## Test Signals
Compile-time structure-size checks would be valuable. Runtime signals include successful firmware version parsing, H2C power/join commands accepted, WFM/firmware command bits clearing, WoWLAN command paths building expected sizes, and firmware compatibility across known 8192SE firmware versions.
