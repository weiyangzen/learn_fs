# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/isp_v4_1_1.h

Purpose: declares the ISP 4.1.1 hardware interface used by the amdgpu ISP block and centralizes constants for memory resources, interrupt resources, and fixed register offsets.

Important APIs and types: includes `amdgpu_isp.h` and ISP IRQ source IDs, defines `MAX_ISP411_MEM_RES`, `MAX_ISP411_INT_SRC`, PHY/I2C/GPIO offsets and sizes, and declares `isp_v4_1_1_set_isp_funcs(struct amdgpu_isp *isp)`.

Control flow and state: this header has no runtime logic or persistent state. Its constants determine the resource array layout that `isp_v4_1_1.c` fills during hardware init: two memory resources followed by eight IRQ resources.

Dependencies and integration: consumed by the ISP v4.1.1 implementation and by amdgpu ISP initialization code that selects generation-specific function tables. The IRQ include ties the implementation to the ISP 4.1 interrupt source namespace.

Risks and test signals: offset or size drift would expose the wrong MMIO ranges to MFD child drivers. Tests should confirm that resource counts match allocation and loops in `isp_v4_1_1_hw_init()`, and that the declared function setter is linked into the owning amdgpu ISP IP selection path.
