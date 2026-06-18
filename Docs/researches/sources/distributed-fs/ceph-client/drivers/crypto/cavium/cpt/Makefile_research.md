# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/Makefile

Purpose: builds the Thunder CPT PF and VF composite objects.

Important APIs and control flow: `obj-$(CONFIG_CAVIUM_CPT) += cptpf.o cptvf.o` emits two modules or built-in objects. `cptpf-objs` links `cptpf_main.o` and `cptpf_mbox.o`; `cptvf-objs` links VF PCI setup, request manager, mailbox, and crypto algorithm registration files.

State and dependencies: no runtime state; it fixes link boundaries so PF and VF PCI drivers register separately but share common headers.

Integration points: selected by `CONFIG_CAVIUM_CPT`, with PF matching PCI device `0xa040` and VF matching `0xa041`.

Risks and test signals: risks include unresolved symbols if object membership drifts and missing algorithm support if `cptvf_algs.o` is omitted. Test signals are successful module link, separate `thunder-cpt` and `thunder-cptvf` PCI driver registration, and crypto algorithms appearing only when VF support initializes.
