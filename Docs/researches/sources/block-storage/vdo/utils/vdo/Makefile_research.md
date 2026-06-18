# File Research: sources/block-storage/vdo/utils/vdo/Makefile

Builds the VDO userspace utility suite and its shared static library `libvdo.a`.

Key details:
- Defines `VDO_VERSION = 8.3.2.1` and passes it as `CURRENT_VERSION`.
- Builds command binaries such as `vdoaudit`, `vdocalculatesize`, `vdodebugmetadata`, `vdodumpblockmap`, `vdodumpmetadata`, `vdoforcerebuild`, `vdoformat`, `vdolistmetadata`, `vdoreadonly`, and `vdostats`.
- Installs script-only/nonbuilt tools `adaptlvm` and `vdorecover`.
- Links against `../uds/libuds.a` plus `dl`, `pthread`, `z`, `rt`, `m`, and `uuid`; `vdoformat` also links `blkid`.
- Uses strict warning policy with `-Werror`, compiler-specific warning suppression for clang, and generated `.deps/*.d` dependency files.

Risk notes:
- `clean` removes local objects, archive, dependencies, and built programs but delegates manpage cleanup to `man`.
- Build behavior depends on UDS library availability in `../uds`.
