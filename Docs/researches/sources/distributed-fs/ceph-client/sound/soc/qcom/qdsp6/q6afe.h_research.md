# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe.h

Purpose: `q6afe.h` is the public interface for the legacy Q6 AFE service. It defines LPASS clock IDs, port limits, channel-map constants, and per-transport configuration structs consumed by `q6afe.c` and DAI drivers.

Important APIs and types: key structs are `q6afe_hdmi_cfg`, `q6afe_slim_cfg`, `q6afe_i2s_cfg`, `q6afe_tdm_cfg`, `q6afe_cdc_dma_cfg`, `q6afe_usb_cfg`, and the aggregate `q6afe_port_config`. The opaque `struct q6afe_port` enforces use through helper functions. Exported declarations cover port acquisition/lifetime, start/stop, virtual-to-DSP port lookup, transport-specific prepare helpers, `q6afe_port_set_sysclk`, global clock setting, codec DMA/TDM preparation, USB device-token programming, and LPASS core vote/unvote.

Control flow: users include this header, call `q6afe_port_get_from_id`, fill one of the transport config structs, call the matching prepare routine, optionally configure clocks or USB device tokens, start the port, then stop and put it. The header does not execute logic but establishes the required order and data contracts for `q6afe.c`.

State and persistence: no state is stored here. The constants are ABI-like DSP command values and must remain stable relative to firmware expectations. Config structs are copied by callers into the runtime port object.

Dependencies and integration points: the header includes `../common.h` for `LPASS_MAX_PORT` and channel/port definitions. It integrates backend DAI implementations with AFE service internals while hiding `struct q6afe_port` fields.

Risks: several clock ID ranges overlap by design, notably PCM/TDM IDs, so callers must pass the correct semantic clock and transport. Channel-map size is fixed at eight, and unsupported layouts require validation before reaching firmware. Changing struct field widths or constant values breaks packed messages built in `q6afe.c`.

Test signals: compile coverage from all AFE DAI users is the primary signal. Runtime tests should verify each declared helper is exported by `q6afe.c` and that expected clock IDs produce firmware-visible clock commands.
