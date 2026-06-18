# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_ih.h

Purpose: exports the CIK interrupt handler IP block descriptor.

Important API: declares `extern const struct amdgpu_ip_block_version cik_ih_ip_block`, used by CIK common setup to add the IH block to the device IP block list.

Control flow: no implementation. `cik_set_ip_blocks()` consumes this symbol during ASIC-specific IP block assembly, after common/GMC and before GFX/SDMA blocks.

State and persistence: stateless header; the referenced block owns IH ring and IRQ state when initialized.

Dependencies and integration points: requires the AMDGPU IP block type definition from includers. Integrates `cik_ih.c` with `cik.c`.

Risks: if the symbol declaration drifts from the definition, CIK IP block registration fails at build/link time. Ordering remains a caller responsibility.

Test signals: link success and runtime IP block list containing the IH block for supported CIK ASICs.
