# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/navi10_ih.h

Purpose: this header declares the Navi10 IH IP block descriptor so ASIC discovery and SOC setup code can add the interrupt-handler block to an AMDGPU device. It is the public interface for `navi10_ih.c`.

Important APIs and types: the only exported symbol is `extern const struct amdgpu_ip_block_version navi10_ih_ip_block;`. That object carries the IP block type, version numbers, and lifecycle function table implemented in `navi10_ih.c`.

Control flow: the header has no runtime logic. Consumers include it, pass `&navi10_ih_ip_block` into AMDGPU IP-block registration, and the common device initialization framework later calls the function table embedded in that descriptor.

State and persistence: there is no state in the header. The declared descriptor is a constant object in the C file; all mutable state lives in `adev->irq` rings, MMIO registers, doorbells, PSP programming state, and common IP-block framework data.

Dependencies and integration: users need the AMDGPU IP block type declarations available before including this header. The declaration is referenced by SOC/discovery code that decides whether Navi10-style IH handling applies to a given GPU. It integrates indirectly with the common interrupt handler through the descriptor's lifecycle callbacks.

Risks: because this header exposes only one descriptor, build or link failures are the primary risk if the C object is omitted from the build. Assigning this descriptor to incompatible hardware would call Navi10 register programming against the wrong OSSSYS register layout. Version changes in `struct amdgpu_ip_block_version` must remain compatible with the definition in `navi10_ih.c`.

Test signals: compile/link coverage should verify the descriptor is built and reachable from discovery/SOC code. Runtime validation is indirect: a device using this descriptor should execute Navi10 IH early/sw/hw init, receive interrupts through the common IH dispatch path, and cleanly suspend/resume/fini.
