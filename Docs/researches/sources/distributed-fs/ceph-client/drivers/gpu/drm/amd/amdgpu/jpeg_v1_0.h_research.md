# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v1_0.h

Purpose: declares the public JPEG v1.0 entry points and the register allowlist constants used by the v1 command submission parser.

Important APIs and types: declares early/software init/fini and `jpeg_v1_0_start()`. Defines the legal v1 register range plus special LMI BAR, context index/data, and soft-reset registers accepted by `jpeg_v1_dec_ring_parse_cs()`.

Control flow and state: no runtime state. The constants directly shape security validation for user-provided JPEG command streams.

Dependencies and integration: included by `jpeg_v1_0.c` and indirectly tied to PACKETJ parsing macros and SOC15 JPEG register numbering.

Risks and test signals: the parser allowlist is a security boundary; incorrect constants can either reject valid UMD streams or allow writes outside the intended JPEG decode register set. Test with valid decode IBs, soft reset packets, NOPs, and malformed register/type combinations.
