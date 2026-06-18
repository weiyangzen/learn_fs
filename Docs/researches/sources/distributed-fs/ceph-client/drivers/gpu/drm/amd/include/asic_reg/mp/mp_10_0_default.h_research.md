# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_10_0_default.h

Purpose: generated AMD MP 10.0 register-default header for the SMU MP0 and MP1 SMN decode blocks. It defines reset/default values for the MP0/MP1 `C2PMSG_32..103` mailbox registers plus interrupt-handler helper registers, giving driver code a compile-time source of expected reset contents for SMU/PSP mailbox state.

Important APIs and state: the exported interface is only preprocessor constants named `mmMP0_SMN_*_DEFAULT` and `mmMP1_SMN_*_DEFAULT`. All listed defaults are `0x00000000`, including the 72 MP0 C2P message slots, the 72 MP1 C2P message slots, `IH_CREDIT`, `IH_SW_INT`, `IH_SW_INT_CTRL`, and MP1-only `FPS_CNT`. There are no C types, functions, inline helpers, or storage objects.

Control flow: none in this file. Compile-time users include it through SMU10 include stacks and then combine these constants with offset and mask headers when they need reset-value comparisons or register-table initialization.

State and persistence: the header does not persist kernel state, but it documents hardware reset state. Runtime state lives in the device registers addressed by the matching offset header; these default macros should not be mistaken for cached software values after firmware, PSP, or SMU command traffic starts mutating the mailbox registers.

Dependencies and integration: guarded by `_mp_10_0_DEFAULT_HEADER` and designed to pair with `mp_10_0_offset.h` and `mp_10_0_sh_mask.h`. In this tree it is pulled by `pm/powerplay/hwmgr/smu10_inc.h`, which exposes MP 10.0 register definitions to the older PowerPlay SMU10 manager path. Consumers typically use AMDGPU register access macros rather than this header directly.

Risks and test signals: because every value is zero, the main risk is assuming a zero default is still valid after firmware boot or after mailbox ownership changes. Regeneration mistakes can silently break register-table code because these macros are untyped and unchecked. Test signals are compile coverage of the SMU10 include path and runtime bring-up on MP 10.0 ASICs where reset-state checks, if present, do not report unexpected nonzero mailbox defaults immediately after reset.
