# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/topaz_pcie_ipc.h

Purpose: defines Topaz PCIe BDA boot states, flags, descriptor constants, DMA address helpers, endian markers, and utility macros used by the Topaz transport.

Important APIs/types/functions: boot states include PCIe init/ready, firmware load ready/done/start/run/config/running, host/target ready, flash boot, QLINK done, block transfer states, and failure states. Flags advertise RC mode, MSI, calibration command, flash presence/boot, bootloader transfer, QLINK driver, target/host errors, and BDA version/error masks. Address macros handle 32-bit/64-bit host values based on `BITS_PER_LONG`. Descriptor constants define TX queue length, valid-packet bit, packet length mask, BD empty/wrap/len/offset fields, RX done interrupt cadence mask, DMA offset error markers, endian detection values, and `NBLOCKS`.

Control flow: `topaz_pcie.c` uses this header to drive the firmware upload state machine, BDA flag negotiation, descriptor parsing/building, RX completion notifications, DMA offset correction, and endian detection handshake.

State and persistence: no C state is stored here; constants describe volatile shared BDA/register state.

Dependencies and integration points: includes Linux types and `shm_ipc_defs.h`. It is Topaz-specific and must remain synchronized with firmware/BDA layout in `qtnf_topaz_bda`.

Risks: state values are used by equality polling, so overlapping or incorrect values cause boot hangs. Descriptor length/offset macros directly control RX packet extraction. `BITS_PER_LONG` address helpers must agree with the DMA mask used by Topaz code. Endian detection markers are part of a fragile pre-boot handshake.

Test signals: 32-bit and 64-bit compile coverage, Topaz boot handshakes for all upload/flashboot branches, descriptor wrap/offset extraction under RX traffic, endian detection success/failure, and `NBLOCKS` block count behavior for firmware sizes around block boundaries.
