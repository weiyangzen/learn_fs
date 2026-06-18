# sources/distributed-fs/ceph-client/drivers/media/common/siano/sms-cards.h

Purpose: board IDs, board metadata structures, board event enum, LED constants, and board-helper prototypes for Siano SMS1xxx devices.

Important APIs/types: defines board ID constants `SMS_BOARD_UNKNOWN` through `SMS1XXX_BOARD_PCTV_77E`; `struct sms_board_gpio_cfg` names many optional GPIO roles; `struct sms_board` stores device type, name, firmware names by mode, GPIO config, RC map, legacy GPIO shortcuts, interface number, default mode, MTU, crystal, and antenna config. Declares board lookup/setup/power/LED/LNA/module-load helpers.

Control flow: header-only declarations; implementation switches on board IDs in `sms-cards.c`.

State/persistence: no state, except `extern struct smscore_device_t *coredev` declaration from surrounding Siano code.

Dependencies/integration: includes `smscoreapi.h`, Linux USB declarations, and `smsir.h`; consumed by Siano core, USB/SDIO, IR, and DVB adaptation code.

Risks/test signals: numeric board IDs are ABI-like within driver tables and transport ID mappings, so reordering is risky. Tests/build checks should ensure array entries exist for all constants, event enum users handle defaults, and optional fields have clear sentinel semantics.
