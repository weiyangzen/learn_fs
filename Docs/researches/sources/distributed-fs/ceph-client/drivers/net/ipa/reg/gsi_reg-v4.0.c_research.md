# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.0.c

Purpose: Defines the GSI register descriptor table for GSI v2.0 / IPA v4.0 hardware.

Important APIs and data: Exports `const struct regs gsi_regs_v4_0`. It keeps the legacy register-window layout while expanding `HW_PARAM_2` to include SDMA capability fields such as `GSI_USE_SDMA`, SDMA interrupt count, maximum burst, and IOVEC count in addition to pending/full-channel flags.

Control flow and integration: GSI setup and command code use this table to program channel contexts, event contexts, QoS, scratch, doorbell, command, status, and interrupt registers. Capability discovery uses the v4.0 `HW_PARAM_2` mask to conditionally configure SDMA-related behavior.

State and persistence: All state is static constant register metadata. Hardware state programmed through the descriptors persists in GSI MMIO registers until reset or reprogramming.

Dependencies: Depends on `gsi_reg.h` ID definitions, `ipa_version.h` execution-environment values, and `reg.h` descriptor helpers.

Risks: v4.0 is a boundary where capability fields broaden but offsets still look like v3.x; treating it as a later v4.5+ map would use wrong base offsets for some blocks. Incorrect SDMA field masks can make capability detection unreliable.

Test signals: Probe IPA v4.0, read and interpret `HW_PARAM_2`, open/close channels and event rings, generate doorbells, and verify IRQ status/mask/clear handling.
