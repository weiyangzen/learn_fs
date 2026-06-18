# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c

## Purpose

`dmub_dcn30.c` provides DCN 3.0 DMUB register metadata and overrides the firmware backdoor-load/window-setup behavior where DCN30 differs from DCN20. It targets Sienna Cichlid style register definitions.

## Important APIs, Types, And Functions

`dmub_srv_dcn30_regs` is the exported common register table for DCN30. Private helpers `dmub_dcn30_get_fb_base_offset` and `dmub_dcn30_translate_addr` mirror DCN20 address translation for firmware load windows.

The exported hardware functions are `dmub_dcn30_backdoor_load` and `dmub_dcn30_setup_windows`.

## Control Flow And Data Flow

Backdoor load reads or uses cached framebuffer base/offset, asserts secure reset, translates CW0 and CW1 addresses, programs REGION3 CW0/CW1 offsets, bases, tops, and enables, then releases secure reset with memory unit ID `0x20`. Unlike DCN20, it does not program `DMCUB_MEM_CNTL` read/write space because that control does not exist on this generation.

Window setup differs more strongly from DCN20. A comment states Sienna Cichlid has hardwired virtual addressing for CW2-CW7, so it uses each window's offset directly instead of translating through framebuffer base/offset. CW2 is disabled when base equals top. CW3, CW5, and CW6 are programmed through REGION3. CW4 uses REGION3_CW4 when `dmub_dcn20_use_cached_inbox()` allows it, otherwise legacy REGION4. CW5 is mirrored into REGION5 as in DCN20.

## State And Persistence Behavior

The file mutates secure reset and code-window MMIO state. It relies on `dmub->soc_fb_info` for optional address translation during backdoor load and `dmub->fw_version` indirectly for cached inbox policy through the DCN20 helper.

## Dependencies And Integration Points

It depends on `dmub_srv.h`, `dmub_reg.h`, `dmub_dcn20.h`, `dmub_dcn30.h`, `sienna_cichlid_ip_offset.h`, and generated DCN 3.0 offset/mask headers. It integrates with the shared `dmub_srv_hw_init` flow via generation-specific function pointers for backdoor load and setup windows, while other operations may reuse DCN20 functions.

## Risks And Edge Cases

Using direct offsets for CW2-CW7 is generation-specific. Applying this function to a generation requiring framebuffer translation would corrupt window programming. Conversely, using DCN20 window translation on DCN30 would break hardwired virtual addressing.

The cached-inbox firmware-version decision is inherited from DCN20. If DCN30 firmware has different constraints, the shared helper could choose the wrong CW4/REGION4 path.

## Test Signals

Validation includes successful DCN30 build with Sienna Cichlid generated headers, firmware backdoor load success, mailbox setup after direct CW programming, command execution through inbox/outbox, and regression tests on firmware versions around the cached-inbox unsupported range.
