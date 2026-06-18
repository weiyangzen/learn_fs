# sources/distributed-fs/ceph-client/sound/soc/sof/xtensa/core.c

Purpose: implements Xtensa-specific SOF DSP crash decoding callbacks for firmware oops and stack dumps.

Important APIs/functions: `xtensa_exception_causes[]` maps Xtensa exception cause IDs to names/descriptions. `xtensa_dsp_oops()` prints the firmware oops header, matched exception cause, and Xtensa registers such as EXCCAUSE, EXCVADDR, PS, SAR, EPC/EPS registers, INTENABLE, and INTERRUPT. `xtensa_stack()` prints stack words in hex lines and, when present, AR register dumps from the oops structure. `sof_xtensa_arch_ops` exports these callbacks as `dsp_arch_ops`.

Control flow/state: stateless; it formats data supplied by SOF crash handling. Stack pointer and AR count come from the firmware oops platform header.

Dependencies/integration: depends on SOF Xtensa UAPI structures and `sof-priv.h` architecture callback plumbing. Exported in namespace `SND_SOC_SOF_XTENSA`.

Risks/test signals: malformed firmware oops data could produce misleading dumps if `stack_words` or `numaregs` do not match allocated data. Tests should inject known oops structures, unknown exception causes, zero AR registers, and stack lengths not multiples of four to validate logging boundaries.
