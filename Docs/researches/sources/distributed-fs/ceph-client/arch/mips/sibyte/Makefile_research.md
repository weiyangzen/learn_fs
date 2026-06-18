# sources/distributed-fs/ceph-client/arch/mips/sibyte/Makefile

Purpose: top-level SiByte platform build routing. It includes common, SB1250, BCM1480, and board-specific SWARM-family directories based on config.

Important APIs and control flow: BCM112x and SB1250 select `sb1250/` plus `common/`; BCM1x80 selects `bcm1480/` plus `common/`. Several board configs select the `swarm/` directory.

State, persistence, and integration: no runtime state; it controls which SoC and board hooks are linked. Dependencies include SoC Kconfig selections and board Kconfig symbols. Risks include missing common firmware code if SoC selections are inconsistent and duplicate directory inclusion controlled by mutually exclusive configs. Test signals are build object lists and successful link for each SiByte board.
