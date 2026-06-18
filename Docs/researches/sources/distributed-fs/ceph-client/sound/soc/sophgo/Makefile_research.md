# sources/distributed-fs/ceph-client/sound/soc/sophgo/Makefile

Purpose: maps Sophgo audio Kconfig symbols to object files.

Important APIs/types: builds `cv1800b-tdm.o`, `cv1800b-sound-adc.o`, and `cv1800b-sound-dac.o` under their respective config symbols.

Control flow/state: no runtime state.

Dependencies/integration: links the CPU DAI and codec drivers into kernel/module builds selected by `sophgo/Kconfig`.

Risks/test signals: verify module names match Kconfig help expectations and that all three drivers build independently.
