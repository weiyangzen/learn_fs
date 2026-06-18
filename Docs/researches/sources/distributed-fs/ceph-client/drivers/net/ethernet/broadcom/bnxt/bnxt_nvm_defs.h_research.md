# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_nvm_defs.h

## Purpose

`bnxt_nvm_defs.h` defines BNXT NVM directory type IDs, directory ordinal/extension/attribute constants, and package-log field indexes used by ethtool NVM and firmware package flows. It is a compact contract between driver code and Broadcom firmware's NVM directory layout.

## Important APIs, types, and macros

- `enum bnxt_nvm_directory_type` names NVM item directory types, including package log, UPDATE area, firmware/patch images for CHIMP/APE/KONG/BONO/TANG, bootcode, VPD, PCIe, external PHY, shared/port/function/management configuration, and management logs.
- `BNX_DIR_ORDINAL_FIRST` is the default ordinal used by lookup and flash helpers.
- `BNX_DIR_EXT_NONE`, `BNX_DIR_EXT_INACTIVE`, and `BNX_DIR_EXT_UPDATE` encode directory extension flags.
- `BNX_DIR_ATTR_NONE`, `BNX_DIR_ATTR_NO_CHKSUM`, and `BNX_DIR_ATTR_PROP_STREAM` encode NVM item attributes.
- `enum bnxnvm_pkglog_field_index` identifies tab-separated package log fields, with package version used by `bnxt_get_pkginfo()`.

## Control flow role

The header is passive. `bnxt_ethtool.c` uses the directory type enum to route flash requests to package, firmware, microcode, or raw NVM write paths; to find UPDATE and PKG_LOG entries; and to decide which firmware reset processor is affected. Package-log field indexes drive in-place parsing of the NVM package log.

## State and persistence behavior

No memory state is stored. These constants identify persistent NVM entries and attributes. Operations using them may create, resize, erase, read, or overwrite NVM contents.

## Dependencies and integration points

- Integrated by `bnxt_ethtool.c` NVM get/set/flash/package helpers.
- Must match firmware-defined NVM directory IDs and package log format.
- Used with HWRM NVM commands such as FIND_DIR_ENTRY, READ, WRITE, MODIFY, INSTALL_UPDATE, DEFRAG, and ERASE_DIR_ENTRY.

## Risks and edge cases

- Directory type numeric values are firmware ABI. Renumbering breaks NVM access and flashing.
- Missing newer directory types can force otherwise valid firmware regions down unsupported/default paths.
- Package-log field indexes assume the firmware log remains tab-separated and stable.
- Executable versus non-executable classification is implemented in `bnxt_ethtool.c`; new enum values need corresponding classification updates.

## Test signals

- NVM directory lookup tests for PKG_LOG and UPDATE entries.
- Flash dispatch tests for every executable directory type.
- Package version parsing tests with complete, missing, malformed, and nonnumeric package version fields.
- Firmware ABI review whenever HWRM/NVM directory definitions are updated.
