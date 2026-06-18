# sources/distributed-fs/ceph-client/arch/arm/kernel/insn.c

Purpose: generates in-memory ARM or Thumb-2 branch opcodes for runtime text patching users such as jump labels and alternatives.

Important APIs/types/functions: `__arm_gen_branch` is the exported core helper; internal `__arm_gen_branch_thumb2` and `__arm_gen_branch_arm` encode BL/B ranges and PC biases. It relies on `__opcode_thumb32_compose` and opcode endianness conversion helpers from `asm/opcodes.h`.

Control flow: callers provide source PC, destination, link flag, and warning policy. The helper selects Thumb-2 or ARM encoding at build time, checks signed branch range, warns once when requested, and returns zero on impossible branches.

State and persistence: stateless; returned opcodes are later persisted by callers into executable kernel text.

Dependencies and integration: feeds `jump_label.c`, ftrace/static key patching, and text patching. Correct PC bias differs by ISA: Thumb-2 uses `pc + 4`, ARM uses `pc + 8`.

Risks: off-by-one range or wrong ISA encoding produces patched control-flow corruption. Test signals include static-key toggling, branch range tests, Thumb-2 and ARM builds, and objdump validation of generated opcodes.
