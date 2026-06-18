## sources/distributed-fs/ceph-client/arch/arm64/include/asm/dcc.h

Purpose: declares debug communications channel console helpers.

Important APIs/types/functions: provides DCC status bit definitions and inline helpers for reading/writing debug channel registers when enabled by low-level debug code.

Control flow: helpers poll status and access debug data registers through sysreg instructions.

State and persistence: interacts with external debug channel hardware; no kernel-persistent state here.

Dependencies and integration: used by early debug/printk or debug monitor code on systems where DCC is available.

Risks: polling or register misuse can hang early boot or lose debug output. Test signals are earlycon/debug-console boots on supported hardware and build coverage with debug configs.
