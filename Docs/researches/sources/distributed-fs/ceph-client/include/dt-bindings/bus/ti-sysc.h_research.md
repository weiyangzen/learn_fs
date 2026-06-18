# sources/distributed-fs/ceph-client/include/dt-bindings/bus/ti-sysc.h

Purpose: defines TI sysc interconnect target-module bit constants and idle-mode values for OMAP/AM/DRA device trees.

Important APIs/types/functions: constants cover OMAP2 clockactivity/emufree/wakeup/softreset/autoidle, OMAP4 DMA disable/freeemu/softreset, SmartReflex wakeup, DRA7 MCAN wakeup, PRUSS standby/submodule wait bits, and `SYSC_IDLE_FORCE`, `SYSC_IDLE_NO`, `SYSC_IDLE_SMART`, `SYSC_IDLE_SMART_WKUP`.

Control flow: DTS sysc nodes encode supported bits and idle modes; the sysc driver writes module SYSCONFIG registers and manages reset/idle transitions.

State and persistence: constants are DT ABI. Runtime state is target-module register configuration.

Dependencies and integration: standalone binding used by TI OMAP/AM/DRA DTS files and sysc interconnect driver.

Risks and test signals: wrong bit values can break reset, wakeup, or idle behavior. Test suspend/resume, module idle transitions, PRUSS and MCAN wakeup, and dt-schema coverage.
