# File Research: sources/block-storage/vdo/utils/vdo/adaptlvm

Bash helper for temporarily exposing an LVMVDO backing volume as writable, then restoring the normal read-only LVMVDO activation.

Key details:
- CLI shape is `adaptlvm [ setRO | setRW ] <volume_group>/<logical_volume>`.
- `setRW` finds the VDO pool name through `lvdisplay`, locates the `_vdata` device-mapper table, deactivates the LVM LV, and creates a temporary `/dev/mapper/${VG}-${LV}` device with the backing table.
- `setRO` removes that temporary mapper device and reactivates the original LV.
- Supports extra LVM flags through `EXTRA_LVM_ARGS`.

Risk notes:
- The device lookup test uses command substitution around `grep -q`; because `grep -q` emits no output, the condition is logically suspect and may always take the “not found” path.
- Installs a trap for `cleanup 2`, but no `cleanup` function is defined in this file.
- Unquoted variable usage appears in several device-manager and LVM commands, so unusual VG/LV names could break parsing or command invocation.
