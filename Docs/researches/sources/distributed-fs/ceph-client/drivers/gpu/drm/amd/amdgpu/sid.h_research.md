# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sid.h

Purpose: Southern Islands hardware definition header. It collects non-generated register offsets, bit masks, packet encoders, display constants, DMA packet formats, memory-controller fields, interrupt-ring fields, and media PLL definitions used by SI-era drivers.

Important APIs, types, and functions: key macros include `SI_MAX_CTLACKS_ASSERTION_WAIT`, UPLL/VCEPLL register fields, VM invalidate registers, IH control registers, PM4 `PACKET0/PACKET3` encoders, SDMA `DMA_PACKET/DMA_IB_PACKET/DMA_PTE_PDE_PACKET`, SDMA packet opcodes, CRTC/HPD/audio offsets, graphics format constants, PCIe indirect index/data registers, and memory type masks.

Control flow: no executable flow. The macro encoders directly shape command processor and SDMA command streams and register programming sequences in SI common, GFX, DCE, GMC, VCE, UVD, and SDMA code.

State and persistence: no state is stored. The constants describe hardware register state and command packet layouts.

Dependencies and integration points: included by `si.c`, `si_dma.c`, `si_ih.c`, and other SI IP files. It bridges hand-maintained SI definitions with generated block-specific headers.

Risks and test signals: incorrect bit shifts or packet formats cause hard-to-debug GPU hangs, invalid display programming, broken DMA copies, or failed PLL changes. Test signals include command submission, SDMA packet execution, display modeset, IH interrupt delivery, UVD/VCE clock changes, memory-controller setup, and VM invalidate success.
