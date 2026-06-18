# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa.h

Purpose: Defines the top-level `struct ipa` driver state and declares `ipa_setup()`, the setup-stage entry point. This header is the central ownership model for IPA core, GSI, power, memory, endpoints, interrupts, modem state, and QMI integration.

Important APIs/types: `struct ipa` embeds `struct gsi`, records hardware version, device, completions, remoteproc notifier, SMP2P/power pointers, route/filter table DMA allocation, interrupt state, microcontroller flags, register mapping, IPA-local memory mapping and descriptor array, IMEM/SMEM IOVAs, zero buffer, endpoint bitmaps, endpoint arrays/maps, setup completion, modem state, netdev, and QMI state. `ipa_setup()` performs setup after GSI firmware readiness.

Control flow and integration: IPA initialization is staged: init without hardware, config with IPA power/register access, and setup after GSI readiness. `ipa_setup()` is called either after TrustZone firmware load or after modem SMP2P readiness. GSI and immediate-command layers use `container_of(trans->gsi, struct ipa, gsi)` to reach this object.

State and persistence: This is the primary mutable state for the IPA driver. It persists for the lifetime of the platform device. Hardware-programmed state is mirrored by bitmaps for endpoint defined/available/set_up/enabled, microcontroller readiness flags, modem state, and memory/register mappings.

Dependencies: Includes GSI, endpoint, memory, QMI, and version headers plus Linux notifier/types. It forward-declares interrupt, power, SMP2P, and netdev types to reduce include coupling.

Risks: Because many subsystems share `struct ipa`, lifecycle ordering is critical. `setup_complete`, modem state, endpoint bitmaps, and GSI channel state must stay consistent through modem SSR and suspend/resume. Table and memory pointers must be valid before immediate commands run.

Test signals: Probe/remove lifecycle, firmware readiness paths, SMP2P-triggered setup, modem SSR notifier behavior, endpoint enable/disable bitmap consistency, and QMI/netdev integration. Failures often show as command timeout, endpoint not found, or table/memory validation logs.
