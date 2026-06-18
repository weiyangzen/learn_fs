# subset-b-004185 research

Grouped research report for the requested rc-core keymap, LIRC bridge, USB MCE, Meson, MediaTek, and Nuvoton IR source files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-nebula.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-nebula.c

Purpose: registers the `RC_MAP_NEBULA` rc-core keytable for the nebula remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table nebula[]` with 55 mappings (0x0000 -> KEY_NUMERIC_0; 0x0036 -> KEY_PC). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(nebula)`, `.rc_proto = RC_PROTO_RC5`, and `.name = RC_MAP_NEBULA`. Module lifecycle is `init_rc_map_nebula` calling `rc_map_register()` and `exit_rc_map_nebula` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_NEBULA`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: KEY_PLAY; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_NEBULA`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_RC5` format. Source comments preserve device-specific labels/quirks such as labelled 'Picture'; 16:9; 14:9; AD; chapter.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_NEBULA` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_RC5`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-nebula.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-nec-terratec-cinergy-xs.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-nec-terratec-cinergy-xs.c

Purpose: registers the `RC_MAP_NEC_TERRATEC_CINERGY_XS` rc-core keytable for the Terratec Cinergy Hybrid T USB XS FM remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table nec_terratec_cinergy_xs[]` with 85 mappings (0x1441 -> KEY_HOME; 0x04eb5c -> KEY_NEXT). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(nec_terratec_cinergy_xs)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_NEC_TERRATEC_CINERGY_XS`. Module lifecycle is `init_rc_map_nec_terratec_cinergy_xs` calling `rc_map_register()` and `exit_rc_map_nec_terratec_cinergy_xs` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_NEC_TERRATEC_CINERGY_XS`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: KEY_BACKSPACE, KEY_BLUE, KEY_CHANNELDOWN, KEY_CHANNELUP, KEY_DOWN, KEY_EPG, KEY_GREEN, KEY_HOME, KEY_INFO, KEY_LEFT, KEY_MUTE, KEY_NEXT, KEY_NUMERIC_0, KEY_NUMERIC_1, KEY_NUMERIC_2, KEY_NUMERIC_3, KEY_NUMERIC_4, KEY_NUMERIC_5, KEY_NUMERIC_6, KEY_NUMERIC_7, KEY_NUMERIC_8, KEY_NUMERIC_9, KEY_OK, KEY_PAUSE, KEY_PLAY, KEY_POWER2, KEY_RECORD, KEY_RED, KEY_REWIND, KEY_RIGHT, KEY_STOP, KEY_TEXT, KEY_UP, KEY_VOLUMEDOWN, KEY_VOLUMEUP, KEY_YELLOW; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_NEC_TERRATEC_CINERGY_XS`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NEC` format. Source comments preserve device-specific labels/quirks such as Terratec Grey IR, with most keys in orange; DVD menu; Teletext; AV; A.B.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_NEC_TERRATEC_CINERGY_XS` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NEC`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-nec-terratec-cinergy-xs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-norwood.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-norwood.c

Purpose: registers the `RC_MAP_NORWOOD` rc-core keytable for the Norwood Micro (non-Pro) TV Tuner remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table norwood[]` with 35 mappings (0x20 -> KEY_NUMERIC_0; 0x65 -> KEY_POWER). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(norwood)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_NORWOOD`. Module lifecycle is `init_rc_map_norwood` calling `rc_map_register()` and `exit_rc_map_norwood` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_NORWOOD`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_NORWOOD`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Keys 0 to 9; Video Source; Open/Close software; 2 Digit Select; Recall.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_NORWOOD` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-norwood.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-npgtech.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-npgtech.c

Purpose: registers the `RC_MAP_NPGTECH` rc-core keytable for the npgtech remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table npgtech[]` with 35 mappings (0x1d -> KEY_SWITCHVIDEOMODE; 0x10 -> KEY_POWER). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(npgtech)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_NPGTECH`. Module lifecycle is `init_rc_map_npgtech` calling `rc_map_register()` and `exit_rc_map_npgtech` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_NPGTECH`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_NPGTECH`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as switch inputs; -/--; Pointing arrow; Maximize/Minimize (yellow); Legacy IR type.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_NPGTECH` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-npgtech.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-odroid.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-odroid.c

Purpose: registers the `RC_MAP_ODROID` rc-core keytable for the HardKernel ODROID remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table odroid[]` with 12 mappings (0xb2dc -> KEY_POWER; 0xb280 -> KEY_VOLUMEUP). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(odroid)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_ODROID`. Module lifecycle is `init_rc_map_odroid` calling `rc_map_register()` and `exit_rc_map_odroid` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_ODROID`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_ODROID`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NEC` format.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_ODROID` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NEC`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-odroid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pctv-sedna.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pctv-sedna.c

Purpose: registers the `RC_MAP_PCTV_SEDNA` rc-core keytable for the pctv-sedna remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table pctv_sedna[]` with 32 mappings (0x00 -> KEY_NUMERIC_0; 0x1f -> KEY_PLAY). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(pctv_sedna)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_PCTV_SEDNA`. Module lifecycle is `init_rc_map_pctv_sedna` calling `rc_map_register()` and `exit_rc_map_pctv_sedna` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_PCTV_SEDNA`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_PCTV_SEDNA`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Recall; Stereo; Source; Snapshot; Time Shift.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_PCTV_SEDNA` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pctv-sedna.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pine64.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pine64.c

Purpose: registers the `RC_MAP_PINE64` rc-core keytable for the Pine64 IR remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table pine64[]` with 25 mappings (0x40404d -> KEY_POWER; 0x404047 -> KEY_EPG). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(pine64)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_PINE64`. Module lifecycle is `init_rc_map_pine64` calling `rc_map_register()` and `exit_rc_map_pine64` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_PINE64`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_PINE64`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NECX` format.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_PINE64` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NECX`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pine64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pinnacle-color.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pinnacle-color.c

Purpose: registers the `RC_MAP_PINNACLE_COLOR` rc-core keytable for the pinnacle-color remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table pinnacle_color[]` with 42 mappings (0x59 -> KEY_MUTE; 0x0a -> KEY_BACKSPACE). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(pinnacle_color)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_PINNACLE_COLOR`. Module lifecycle is `init_rc_map_pinnacle_color` calling `rc_map_register()` and `exit_rc_map_pinnacle_color` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_PINNACLE_COLOR`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_PINNACLE_COLOR`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Legacy IR type.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_PINNACLE_COLOR` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pinnacle-color.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pinnacle-grey.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pinnacle-grey.c

Purpose: registers the `RC_MAP_PINNACLE_GREY` rc-core keytable for the pinnacle-grey remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table pinnacle_grey[]` with 41 mappings (0x3a -> KEY_NUMERIC_0; 0x18 -> KEY_EPG). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(pinnacle_grey)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_PINNACLE_GREY`. Module lifecycle is `init_rc_map_pinnacle_grey` calling `rc_map_register()` and `exit_rc_map_pinnacle_grey` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_PINNACLE_GREY`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_PINNACLE_GREY`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Legacy IR type.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_PINNACLE_GREY` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pinnacle-grey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pinnacle-pctv-hd.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pinnacle-pctv-hd.c

Purpose: registers the `RC_MAP_PINNACLE_PCTV_HD` rc-core keytable for the Pinnacle PCTV HD 800i mini remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table pinnacle_pctv_hd[]` with 26 mappings (0x0700 -> KEY_MUTE; 0x073f -> KEY_HELP). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(pinnacle_pctv_hd)`, `.rc_proto = RC_PROTO_RC5`, and `.name = RC_MAP_PINNACLE_PCTV_HD`. Module lifecycle is `init_rc_map_pinnacle_pctv_hd` calling `rc_map_register()` and `exit_rc_map_pinnacle_pctv_hd` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_PINNACLE_PCTV_HD`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_PINNACLE_PCTV_HD`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_RC5` format. Source comments preserve device-specific labels/quirks such as Pinnacle PCTV HD 800i mini remote; Key codes for the tiny Pinnacle remote; Pinnacle logo; 'Square' key; 'T' key.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_PINNACLE_PCTV_HD` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_RC5`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pinnacle-pctv-hd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pixelview-002t.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pixelview-002t.c

Purpose: registers the `RC_MAP_PIXELVIEW_002T` rc-core keytable for the 002-T IR remote keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table pixelview_002t[]` with 26 mappings (0x866b13 -> KEY_MUTE; 0x866b1a -> KEY_STOP). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(pixelview_002t)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_PIXELVIEW_002T`. Module lifecycle is `init_rc_map_pixelview` calling `rc_map_register()` and `exit_rc_map_pixelview` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_PIXELVIEW_002T`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_PIXELVIEW_002T`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NECX` format. Source comments preserve device-specific labels/quirks such as power; vol +; vol -; snapshot; zoom.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_PIXELVIEW_002T` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NECX`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pixelview-002t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pixelview-mk12.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pixelview-mk12.c

Purpose: registers the `RC_MAP_PIXELVIEW_MK12` rc-core keytable for the MK-F12 IR remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table pixelview_mk12[]` with 31 mappings (0x866b03 -> KEY_TUNER; 0x866b07 -> KEY_RADIO). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(pixelview_mk12)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_PIXELVIEW_MK12`. Module lifecycle is `init_rc_map_pixelview` calling `rc_map_register()` and `exit_rc_map_pixelview` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_PIXELVIEW_MK12`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_PIXELVIEW_MK12`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NECX` format. Source comments preserve device-specific labels/quirks such as Timeshift; power; loop; +100; source.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_PIXELVIEW_MK12` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NECX`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pixelview-mk12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pixelview-new.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pixelview-new.c

Purpose: registers the `RC_MAP_PIXELVIEW_NEW` rc-core keytable for the pixelview-new remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table pixelview_new[]` with 31 mappings (0x3c -> KEY_TIME; 0x34 -> KEY_RADIO). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(pixelview_new)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_PIXELVIEW_NEW`. Module lifecycle is `init_rc_map_pixelview_new` calling `rc_map_register()` and `exit_rc_map_pixelview_new` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_PIXELVIEW_NEW`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_PIXELVIEW_NEW`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Timeshift; LOOP; Source; +100; SNAPSHOT.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_PIXELVIEW_NEW` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pixelview-new.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pixelview.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pixelview.c

Purpose: registers the `RC_MAP_PIXELVIEW` rc-core keytable for the pixelview remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table pixelview[]` with 32 mappings (0x1e -> KEY_POWER; 0x18 -> KEY_MUTE). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(pixelview)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_PIXELVIEW`. Module lifecycle is `init_rc_map_pixelview` calling `rc_map_register()` and `exit_rc_map_pixelview` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_PIXELVIEW`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_PIXELVIEW`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as power; source; scan; TV/FM; freeze.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_PIXELVIEW` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pixelview.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-powercolor-real-angel.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-powercolor-real-angel.c

Purpose: registers the `RC_MAP_POWERCOLOR_REAL_ANGEL` rc-core keytable for the Powercolor Real Angel 330 remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table powercolor_real_angel[]` with 35 mappings (0x38 -> KEY_SWITCHVIDEOMODE; 0x25 -> KEY_POWER). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(powercolor_real_angel)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_POWERCOLOR_REAL_ANGEL`. Module lifecycle is `init_rc_map_powercolor_real_angel` calling `rc_map_register()` and `exit_rc_map_powercolor_real_angel` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_POWERCOLOR_REAL_ANGEL`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_POWERCOLOR_REAL_ANGEL`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as switch inputs; Turn ON/OFF App; single, double, triple digit; previous channel; stereo/mono.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_POWERCOLOR_REAL_ANGEL` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-powercolor-real-angel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-proteus-2309.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-proteus-2309.c

Purpose: registers the `RC_MAP_PROTEUS_2309` rc-core keytable for the proteus-2309 remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table proteus_2309[]` with 24 mappings (0x00 -> KEY_NUMERIC_0; 0x14 -> KEY_F1). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(proteus_2309)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_PROTEUS_2309`. Module lifecycle is `init_rc_map_proteus_2309` calling `rc_map_register()` and `exit_rc_map_proteus_2309` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_PROTEUS_2309`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_PROTEUS_2309`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Michal Majchrowicz <mmajchrowicz@gmail.com>; numeric; power; full screen; recall.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_PROTEUS_2309` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-proteus-2309.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-purpletv.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-purpletv.c

Purpose: registers the `RC_MAP_PURPLETV` rc-core keytable for the purpletv remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table purpletv[]` with 35 mappings (0x03 -> KEY_POWER; 0x42 -> KEY_REWIND). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(purpletv)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_PURPLETV`. Module lifecycle is `init_rc_map_purpletv` calling `rc_map_register()` and `exit_rc_map_purpletv` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_PURPLETV`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_PURPLETV`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Recall; 100+; Video source; Snapshot; MTS Select.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_PURPLETV` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-purpletv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pv951.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pv951.c

Purpose: registers the `RC_MAP_PV951` rc-core keytable for the pv951 remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table pv951[]` with 31 mappings (0x00 -> KEY_NUMERIC_0; 0x1c -> KEY_TV). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(pv951)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_PV951`. Module lifecycle is `init_rc_map_pv951` calling `rc_map_register()` and `exit_rc_map_pv951` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_PV951`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: KEY_TV; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_PV951`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Mark Phalan <phalanm@o2.ie>; CH +/-; CC; TTX; AIR/CBL.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_PV951` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-pv951.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-rc6-mce.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-rc6-mce.c

Purpose: registers the `RC_MAP_RC6_MCE` rc-core keytable for the rc6 MCE remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table rc6_mce[]` with 64 mappings (0x800f0400 -> KEY_NUMERIC_0; 0x800f0481 -> KEY_PLAYPAUSE). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(rc6_mce)`, `.rc_proto = RC_PROTO_RC6_MCE`, and `.name = RC_MAP_RC6_MCE`. Module lifecycle is `init_rc_map_rc6_mce` calling `rc_map_register()` and `exit_rc_map_rc6_mce` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_RC6_MCE`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: KEY_PLAYPAUSE; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_RC6_MCE`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_RC6_MCE` format. Source comments preserve device-specific labels/quirks such as Formerly PC Power; Windows MCE button; LiveTV; Guide; Aspect.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_RC6_MCE` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_RC6_MCE`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-rc6-mce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-real-audio-220-32-keys.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-real-audio-220-32-keys.c

Purpose: registers the `RC_MAP_REAL_AUDIO_220_32_KEYS` rc-core keytable for the Zogis Real Audio 220 - 32 keys remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table real_audio_220_32_keys[]` with 28 mappings (0x1c -> KEY_RADIO; 0x19 -> KEY_CAMERA). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(real_audio_220_32_keys)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_REAL_AUDIO_220_32_KEYS`. Module lifecycle is `init_rc_map_real_audio_220_32_keys` calling `rc_map_register()` and `exit_rc_map_real_audio_220_32_keys` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_REAL_AUDIO_220_32_KEYS`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_REAL_AUDIO_220_32_KEYS`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Zogis Real Audio 220 - 32 keys IR; Source; stereo; Prev; Timeshift.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_REAL_AUDIO_220_32_KEYS` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-real-audio-220-32-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-reddo.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-reddo.c

Purpose: registers the `RC_MAP_REDDO` rc-core keytable for the reddo remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table reddo[]` with 23 mappings (0x61d601 -> KEY_EPG; 0x61d643 -> KEY_POWER2). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(reddo)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_REDDO`. Module lifecycle is `init_rc_map_reddo` calling `rc_map_register()` and `exit_rc_map_reddo` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_REDDO`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_REDDO`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NECX` format. Source comments preserve device-specific labels/quirks such as EPG; CH-; CH+; Zoom; Vol+.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_REDDO` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NECX`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-reddo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-siemens-gigaset-rc20.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-siemens-gigaset-rc20.c

Purpose: registers the `RC_MAP_SIEMENS_GIGASET_RC20` rc-core keytable for the Siemens Gigaset RC20 remote keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table siemens_gigaset_rc20[]` with 33 mappings (0x1501 -> KEY_POWER; 0x1527 -> KEY_INFO). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(siemens_gigaset_rc20)`, `.rc_proto = RC_PROTO_RC5`, and `.name = RC_MAP_SIEMENS_GIGASET_RC20`. Module lifecycle is `init_rc_map_siemens_gigaset_rc20` calling `rc_map_register()` and `exit_rc_map_siemens_gigaset_rc20` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_SIEMENS_GIGASET_RC20`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_SIEMENS_GIGASET_RC20`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_RC5` format. Source comments preserve device-specific labels/quirks such as double-arrow; OPT; TV/Radio.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_SIEMENS_GIGASET_RC20` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_RC5`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-siemens-gigaset-rc20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-snapstream-firefly.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-snapstream-firefly.c

Purpose: registers the `RC_MAP_SNAPSTREAM_FIREFLY` rc-core keytable for the SnapStream Firefly X10 RF remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table snapstream_firefly[]` with 48 mappings (0x2c -> KEY_ZOOM; 0x23 -> KEY_D). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(snapstream_firefly)`, `.rc_proto = RC_PROTO_OTHER`, and `.name = RC_MAP_SNAPSTREAM_FIREFLY`. Module lifecycle is `init_rc_map_snapstream_firefly` calling `rc_map_register()` and `exit_rc_map_snapstream_firefly` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_SNAPSTREAM_FIREFLY`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_SNAPSTREAM_FIREFLY`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_OTHER` format. Source comments preserve device-specific labels/quirks such as Maximize; ent; firefly; Music; Photos.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_SNAPSTREAM_FIREFLY` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_OTHER`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-snapstream-firefly.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-streamzap.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-streamzap.c

Purpose: registers the `RC_MAP_STREAMZAP` rc-core keytable for the Streamzap remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table streamzap[]` with 35 mappings (0x28c0 -> KEY_NUMERIC_0; 0x28e3 -> KEY_BLUE). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(streamzap)`, `.rc_proto = RC_PROTO_RC5_SZ`, and `.name = RC_MAP_STREAMZAP`. Module lifecycle is `init_rc_map_streamzap` calling `rc_map_register()` and `exit_rc_map_streamzap` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_STREAMZAP`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_STREAMZAP`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_RC5_SZ` format.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_STREAMZAP` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_RC5_SZ`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-streamzap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-su3000.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-su3000.c

Purpose: registers the `RC_MAP_SU3000` rc-core keytable for the Geniatech HDStar remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table su3000[]` with 35 mappings (0x25 -> KEY_POWER; 0x0c -> KEY_ESC). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(su3000)`, `.rc_proto = RC_PROTO_RC5`, and `.name = RC_MAP_SU3000`. Module lifecycle is `init_rc_map_su3000` calling `rc_map_register()` and `exit_rc_map_su3000` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_SU3000`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_SU3000`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_RC5` format. Source comments preserve device-specific labels/quirks such as right-bottom Red; -/--; CH+; CH+; Brightness Up.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_SU3000` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_RC5`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-su3000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tanix-tx3mini.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tanix-tx3mini.c

Purpose: registers the `RC_MAP_TANIX_TX3MINI` rc-core keytable for the Tanix TX3 mini STB remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table tanix_tx3mini[]` with 31 mappings (0x8051 -> KEY_POWER; 0x8044 -> KEY_DELETE). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(tanix_tx3mini)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_TANIX_TX3MINI`. Module lifecycle is `init_rc_map_tanix_tx3mini` calling `rc_map_register()` and `exit_rc_map_tanix_tx3mini` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TANIX_TX3MINI`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TANIX_TX3MINI`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NEC` format. Source comments preserve device-specific labels/quirks such as * Keymap for the Tanix TX3 mini STB remote control.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TANIX_TX3MINI` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NEC`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tanix-tx3mini.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tanix-tx5max.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tanix-tx5max.c

Purpose: registers the `RC_MAP_TANIX_TX5MAX` rc-core keytable for the Tanix TX5 max STB remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table tanix_tx5max[]` with 24 mappings (0x40404d -> KEY_POWER; 0x40400c -> KEY_DELETE). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(tanix_tx5max)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_TANIX_TX5MAX`. Module lifecycle is `init_rc_map_tanix_tx5max` calling `rc_map_register()` and `exit_rc_map_tanix_tx5max` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TANIX_TX5MAX`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TANIX_TX5MAX`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NECX` format. Source comments preserve device-specific labels/quirks such as * Keymap for the Tanix TX5 max STB remote control.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TANIX_TX5MAX` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NECX`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tanix-tx5max.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tbs-nec.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tbs-nec.c

Purpose: registers the `RC_MAP_TBS_NEC` rc-core keytable for the tbs-nec remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table tbs_nec[]` with 34 mappings (0x84 -> KEY_POWER2; 0x9b -> KEY_MODE). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(tbs_nec)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_TBS_NEC`. Module lifecycle is `init_rc_map_tbs_nec` calling `rc_map_register()` and `exit_rc_map_tbs_nec` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TBS_NEC`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TBS_NEC`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as power; mute; 10+; 10-; ch+.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TBS_NEC` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tbs-nec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-technisat-ts35.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-technisat-ts35.c

Purpose: registers the `RC_MAP_TECHNISAT_TS35` rc-core keytable for the TechniSat TS35 remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table technisat_ts35[]` with 33 mappings (0x32 -> KEY_MUTE; 0x30 -> KEY_HELP). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(technisat_ts35)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_TECHNISAT_TS35`. Module lifecycle is `init_rc_map` calling `rc_map_register()` and `exit_rc_map` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TECHNISAT_TS35`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TECHNISAT_TS35`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TECHNISAT_TS35` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-technisat-ts35.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-technisat-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-technisat-usb2.c

Purpose: registers the `RC_MAP_TECHNISAT_USB2` rc-core keytable for the TechniSat TS35 remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table technisat_usb2[]` with 33 mappings (0x0a0c -> KEY_POWER; 0x0a0a -> KEY_PROGRAM). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(technisat_usb2)`, `.rc_proto = RC_PROTO_RC5`, and `.name = RC_MAP_TECHNISAT_USB2`. Module lifecycle is `init_rc_map` calling `rc_map_register()` and `exit_rc_map` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TECHNISAT_USB2`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TECHNISAT_USB2`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_RC5` format. Source comments preserve device-specific labels/quirks such as EXT; HOOK.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TECHNISAT_USB2` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_RC5`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-technisat-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-cinergy-c-pci.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-cinergy-c-pci.c

Purpose: registers the `RC_MAP_TERRATEC_CINERGY_C_PCI` rc-core keytable for the Terratec Cinergy C PCI remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table terratec_cinergy_c_pci[]` with 48 mappings (0x3e -> KEY_POWER; 0x03 -> KEY_NEXT). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(terratec_cinergy_c_pci)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_TERRATEC_CINERGY_C_PCI`. Module lifecycle is `init_rc_map_terratec_cinergy_c_pci` calling `rc_map_register()` and `exit_rc_map_terratec_cinergy_c_pci` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TERRATEC_CINERGY_C_PCI`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TERRATEC_CINERGY_C_PCI`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as AV; DVD Menu; Teletext; Music; Pic.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TERRATEC_CINERGY_C_PCI` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-cinergy-c-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-cinergy-s2-hd.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-cinergy-s2-hd.c

Purpose: registers the `RC_MAP_TERRATEC_CINERGY_S2_HD` rc-core keytable for the Terratec Cinergy S2 HD remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table terratec_cinergy_s2_hd[]` with 48 mappings (0x03 -> KEY_NEXT; 0x3e -> KEY_POWER). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(terratec_cinergy_s2_hd)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_TERRATEC_CINERGY_S2_HD`. Module lifecycle is `init_rc_map_terratec_cinergy_s2_hd` calling `rc_map_register()` and `exit_rc_map_terratec_cinergy_s2_hd` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TERRATEC_CINERGY_S2_HD`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TERRATEC_CINERGY_S2_HD`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as keytable for Terratec Cinergy S2 HD Remote Controller; >|; |<; >>; <<.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TERRATEC_CINERGY_S2_HD` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-cinergy-s2-hd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-cinergy-xs.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-cinergy-xs.c

Purpose: registers the `RC_MAP_TERRATEC_CINERGY_XS` rc-core keytable for the Terratec Cinergy Hybrid T USB XS remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table terratec_cinergy_xs[]` with 47 mappings (0x41 -> KEY_HOME; 0x5c -> KEY_NEXT). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(terratec_cinergy_xs)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_TERRATEC_CINERGY_XS`. Module lifecycle is `init_rc_map_terratec_cinergy_xs` calling `rc_map_register()` and `exit_rc_map_terratec_cinergy_xs` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TERRATEC_CINERGY_XS`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TERRATEC_CINERGY_XS`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Legacy IR type.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TERRATEC_CINERGY_XS` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-cinergy-xs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-slim-2.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-slim-2.c

Purpose: registers the `RC_MAP_TERRATEC_SLIM_2` rc-core keytable for the TerraTec slim remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table terratec_slim_2[]` with 18 mappings (0x8001 -> KEY_MUTE; 0x801f -> KEY_NUMERIC_9). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(terratec_slim_2)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_TERRATEC_SLIM_2`. Module lifecycle is `init_rc_map_terratec_slim_2` calling `rc_map_register()` and `exit_rc_map_terratec_slim_2` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TERRATEC_SLIM_2`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TERRATEC_SLIM_2`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NEC` format. Source comments preserve device-specific labels/quirks such as MUTE; [fullscreen]; [two arrows forming a circle]; [red power button].

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TERRATEC_SLIM_2` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NEC`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-slim-2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-slim.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-slim.c

Purpose: registers the `RC_MAP_TERRATEC_SLIM` rc-core keytable for the TerraTec slim remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table terratec_slim[]` with 28 mappings (0x02bd00 -> KEY_NUMERIC_1; 0x02bd45 -> KEY_POWER2). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(terratec_slim)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_TERRATEC_SLIM`. Module lifecycle is `init_rc_map_terratec_slim` calling `rc_map_register()` and `exit_rc_map_terratec_slim` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TERRATEC_SLIM`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TERRATEC_SLIM`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NECX` format. Source comments preserve device-specific labels/quirks such as TerraTec slim remote, 7 rows, 4 columns.; Uses NEC extended 0x02bd.; symbol: PIP; snapshot; [red power button].

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TERRATEC_SLIM` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NECX`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-terratec-slim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tevii-nec.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tevii-nec.c

Purpose: registers the `RC_MAP_TEVII_NEC` rc-core keytable for the tevii-nec remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table tevii_nec[]` with 47 mappings (0x0a -> KEY_POWER2; 0x58 -> KEY_SWITCHVIDEOMODE). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(tevii_nec)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_TEVII_NEC`. Module lifecycle is `init_rc_map_tevii_nec` calling `rc_map_register()` and `exit_rc_map_tevii_nec` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TEVII_NEC`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TEVII_NEC`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Legacy IR type.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TEVII_NEC` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tevii-nec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tivo.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tivo.c

Purpose: registers the `RC_MAP_TIVO` rc-core keytable for the TiVo remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table tivo[]` with 45 mappings (0x3085f009 -> KEY_MEDIA; 0x3085c032 -> KEY_CLEAR). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(tivo)`, `.rc_proto = RC_PROTO_NEC32`, and `.name = RC_MAP_TIVO`. Module lifecycle is `init_rc_map_tivo` calling `rc_map_register()` and `exit_rc_map_tivo` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TIVO`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: KEY_CHANNELDOWN, KEY_CYCLEWINDOWS, KEY_NUMERIC_8; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TIVO`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NEC32` format. Source comments preserve device-specific labels/quirks such as TiVo Button; TV Power; Live TV/Swap; TV Input; Window.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TIVO` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NEC32`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tivo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-total-media-in-hand-02.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-total-media-in-hand-02.c

Purpose: registers the `RC_MAP_TOTAL_MEDIA_IN_HAND_02` rc-core keytable for the Total Media In Hand_02 remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table total_media_in_hand_02[]` with 35 mappings (0x0000 -> KEY_NUMERIC_0; 0x0038 -> KEY_VIDEO). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(total_media_in_hand_02)`, `.rc_proto = RC_PROTO_RC5`, and `.name = RC_MAP_TOTAL_MEDIA_IN_HAND_02`. Module lifecycle is `init_rc_map_total_media_in_hand_02` calling `rc_map_register()` and `exit_rc_map_total_media_in_hand_02` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TOTAL_MEDIA_IN_HAND_02`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TOTAL_MEDIA_IN_HAND_02`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_RC5` format. Source comments preserve device-specific labels/quirks such as Stop; Turn on/off application; OK; Snapshot; Full Screen/Restore.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TOTAL_MEDIA_IN_HAND_02` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_RC5`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-total-media-in-hand-02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-total-media-in-hand.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-total-media-in-hand.c

Purpose: registers the `RC_MAP_TOTAL_MEDIA_IN_HAND` rc-core keytable for the Total Media In Hand remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table total_media_in_hand[]` with 35 mappings (0x02bd00 -> KEY_NUMERIC_1; 0x02bd45 -> KEY_INFO). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(total_media_in_hand)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_TOTAL_MEDIA_IN_HAND`. Module lifecycle is `init_rc_map_total_media_in_hand` calling `rc_map_register()` and `exit_rc_map_total_media_in_hand` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TOTAL_MEDIA_IN_HAND`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TOTAL_MEDIA_IN_HAND`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NECX` format. Source comments preserve device-specific labels/quirks such as Uses NEC extended 0x02bd; yellow, [min / max]; TV / AV; TimeShift; right arrow.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TOTAL_MEDIA_IN_HAND` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NECX`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-total-media-in-hand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-trekstor.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-trekstor.c

Purpose: registers the `RC_MAP_TREKSTOR` rc-core keytable for the TrekStor remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table trekstor[]` with 28 mappings (0x0084 -> KEY_NUMERIC_0; 0x009f -> KEY_LEFT). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(trekstor)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_TREKSTOR`. Module lifecycle is `init_rc_map_trekstor` calling `rc_map_register()` and `exit_rc_map_trekstor` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TREKSTOR`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TREKSTOR`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NEC` format. Source comments preserve device-specific labels/quirks such as TrekStor DVB-T USB Stick remote controller.; Mute; Home; Up; OK.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TREKSTOR` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NEC`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-trekstor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tt-1500.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tt-1500.c

Purpose: registers the `RC_MAP_TT_1500` rc-core keytable for the Technotrend 1500 remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table tt_1500[]` with 39 mappings (0x1501 -> KEY_POWER; 0x153f -> KEY_FORWARD). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(tt_1500)`, `.rc_proto = RC_PROTO_RC5`, and `.name = RC_MAP_TT_1500`. Module lifecycle is `init_rc_map_tt_1500` calling `rc_map_register()` and `exit_rc_map_tt_1500` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TT_1500`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TT_1500`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_RC5` format. Source comments preserve device-specific labels/quirks such as for the Technotrend 1500 bundled remotes (grey and black):; ? double-arrow key; ? TV/Radio; these keys are only in the black remote.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TT_1500` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_RC5`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-tt-1500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-twinhan-dtv-cab-ci.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-twinhan-dtv-cab-ci.c

Purpose: registers the `RC_MAP_TWINHAN_DTV_CAB_CI` rc-core keytable for the Twinhan DTV CAB CI remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table twinhan_dtv_cab_ci[]` with 53 mappings (0x29 -> KEY_POWER; 0x00 -> KEY_BLUE). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(twinhan_dtv_cab_ci)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_TWINHAN_DTV_CAB_CI`. Module lifecycle is `init_rc_map_twinhan_dtv_cab_ci` calling `rc_map_register()` and `exit_rc_map_twinhan_dtv_cab_ci` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TWINHAN_DTV_CAB_CI`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TWINHAN_DTV_CAB_CI`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Preview; Record List; Replay |<; Skip   >|; Capture.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TWINHAN_DTV_CAB_CI` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-twinhan-dtv-cab-ci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-twinhan1027.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-twinhan1027.c

Purpose: registers the `RC_MAP_TWINHAN_VP1027_DVBS` rc-core keytable for the twinhan1027 remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table twinhan_vp1027[]` with 53 mappings (0x16 -> KEY_POWER2; 0x5f -> KEY_BLUE). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(twinhan_vp1027)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_TWINHAN_VP1027_DVBS`. Module lifecycle is `init_rc_map_twinhan_vp1027` calling `rc_map_register()` and `exit_rc_map_twinhan_vp1027` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_TWINHAN_VP1027_DVBS`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_TWINHAN_VP1027_DVBS`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NEC` format.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_TWINHAN_VP1027_DVBS` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NEC`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-twinhan1027.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-vega-s9x.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-vega-s9x.c

Purpose: registers the `RC_MAP_VEGA_S9X` rc-core keytable for the Tronsmart Vega S9x remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table vega_s9x[]` with 13 mappings (0x18 -> KEY_POWER; 0x10 -> KEY_VOLUMEUP). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(vega_s9x)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_VEGA_S9X`. Module lifecycle is `init_rc_map_vega_s9x` calling `rc_map_register()` and `exit_rc_map_vega_s9x` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_VEGA_S9X`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_VEGA_S9X`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NEC` format.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_VEGA_S9X` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NEC`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-vega-s9x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-videomate-m1f.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-videomate-m1f.c

Purpose: registers the `RC_MAP_VIDEOMATE_K100` rc-core keytable for the videomate-m1f remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table videomate_k100[]` with 51 mappings (0x01 -> KEY_POWER; 0x18 -> KEY_TEXT). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(videomate_k100)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_VIDEOMATE_K100`. Module lifecycle is `init_rc_map_videomate_k100` calling `rc_map_register()` and `exit_rc_map_videomate_k100` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_VIDEOMATE_K100`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_VIDEOMATE_K100`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as TV record button; '...' button; WIN key; * key; # key.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_VIDEOMATE_K100` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-videomate-m1f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-videomate-s350.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-videomate-s350.c

Purpose: registers the `RC_MAP_VIDEOMATE_S350` rc-core keytable for the videomate-s350 remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table videomate_s350[]` with 44 mappings (0x00 -> KEY_TV; 0x20 -> KEY_TEXT). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(videomate_s350)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_VIDEOMATE_S350`. Module lifecycle is `init_rc_map_videomate_s350` calling `rc_map_register()` and `exit_rc_map_videomate_s350` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_VIDEOMATE_S350`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_VIDEOMATE_S350`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as TV/Video; Recall; CC; MTS; SURF.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_VIDEOMATE_S350` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-videomate-s350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-videomate-tv-pvr.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-videomate-tv-pvr.c

Purpose: registers the `RC_MAP_VIDEOMATE_TV_PVR` rc-core keytable for the videomate-tv-pvr remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table videomate_tv_pvr[]` with 37 mappings (0x14 -> KEY_MUTE; 0x21 -> KEY_SLEEP). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(videomate_tv_pvr)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_VIDEOMATE_TV_PVR`. Module lifecycle is `init_rc_map_videomate_tv_pvr` calling `rc_map_register()` and `exit_rc_map_videomate_tv_pvr` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_VIDEOMATE_TV_PVR`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_VIDEOMATE_TV_PVR`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Legacy IR type.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_VIDEOMATE_TV_PVR` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-videomate-tv-pvr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-videostrong-kii-pro.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-videostrong-kii-pro.c

Purpose: registers the `RC_MAP_KII_PRO` rc-core keytable for the Videostrong KII Pro STB remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table kii_pro[]` with 45 mappings (0x59 -> KEY_POWER; 0x51 -> KEY_BACKSPACE). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(kii_pro)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_KII_PRO`. Module lifecycle is `init_rc_map_kii_pro` calling `rc_map_register()` and `exit_rc_map_kii_pro` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_KII_PRO`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_KII_PRO`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NEC` format.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_KII_PRO` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NEC`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-videostrong-kii-pro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-wetek-hub.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-wetek-hub.c

Purpose: registers the `RC_MAP_WETEK_HUB` rc-core keytable for the WeTek Hub STB remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table wetek_hub[]` with 12 mappings (0x77f1 -> KEY_POWER; 0x77fc -> KEY_VOLUMEDOWN). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(wetek_hub)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_WETEK_HUB`. Module lifecycle is `init_rc_map_wetek_hub` calling `rc_map_register()` and `exit_rc_map_wetek_hub` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_WETEK_HUB`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_WETEK_HUB`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NEC` format. Source comments preserve device-specific labels/quirks such as * This keymap is used with the WeTek Hub STB..

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_WETEK_HUB` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NEC`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-wetek-hub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-wetek-play2.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-wetek-play2.c

Purpose: registers the `RC_MAP_WETEK_PLAY2` rc-core keytable for the WeTek Play 2 STB remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table wetek_play2[]` with 43 mappings (0x5e5f02 -> KEY_POWER; 0x5e5f2b -> KEY_STOP). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(wetek_play2)`, `.rc_proto = RC_PROTO_NECX`, and `.name = RC_MAP_WETEK_PLAY2`. Module lifecycle is `init_rc_map_wetek_play2` calling `rc_map_register()` and `exit_rc_map_wetek_play2` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_WETEK_PLAY2`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: KEY_BACK; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_WETEK_PLAY2`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NECX` format.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_WETEK_PLAY2` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NECX`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-wetek-play2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-winfast-usbii-deluxe.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-winfast-usbii-deluxe.c

Purpose: registers the `RC_MAP_WINFAST_USBII_DELUXE` rc-core keytable for the Leadtek Winfast TV USB II Deluxe remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table winfast_usbii_deluxe[]` with 28 mappings (0x62 -> KEY_NUMERIC_0; 0x63 -> KEY_ENTER). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(winfast_usbii_deluxe)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_WINFAST_USBII_DELUXE`. Module lifecycle is `init_rc_map_winfast_usbii_deluxe` calling `rc_map_register()` and `exit_rc_map_winfast_usbii_deluxe` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_WINFAST_USBII_DELUXE`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_WINFAST_USBII_DELUXE`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as SNAPSHOT; RECORD; TIMESHIFT; VOLUMEUP; VOLUMEDOWN.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_WINFAST_USBII_DELUXE` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-winfast-usbii-deluxe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-winfast.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-winfast.c

Purpose: registers the `RC_MAP_WINFAST` rc-core keytable for the Leadtek Winfast remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table winfast[]` with 56 mappings (0x12 -> KEY_NUMERIC_0; 0x3f -> KEY_CHANNELDOWN). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(winfast)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_WINFAST`. Module lifecycle is `init_rc_map_winfast` calling `rc_map_register()` and `exit_rc_map_winfast` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_WINFAST`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_WINFAST`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_UNKNOWN` format. Source comments preserve device-specific labels/quirks such as Table for Leadtek Winfast Remote Controls - used by both bttv and cx88; Keys 0 to 9; Audio Source; TV/FM, not on Y0400052; Video Source.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_WINFAST` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_UNKNOWN`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-winfast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-x96max.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-x96max.c

Purpose: registers the `RC_MAP_X96MAX` rc-core keytable for the X96-max STB remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table x96max[]` with 28 mappings (0x140 -> KEY_POWER; 0x104 -> KEY_NUMERIC_9). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(x96max)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_X96MAX`. Module lifecycle is `init_rc_map_x96max` calling `rc_map_register()` and `exit_rc_map_x96max` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_X96MAX`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_X96MAX`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NEC` format.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_X96MAX` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NEC`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-x96max.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-xbox-360.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-xbox-360.c

Purpose: registers the `RC_MAP_XBOX_360` rc-core keytable for the Xbox 360 Universal Media remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table xbox_360[]` with 45 mappings (0x800f7428 -> KEY_EJECTCD; 0x800f741c -> KEY_CANCEL). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(xbox_360)`, `.rc_proto = RC_PROTO_RC6_MCE`, and `.name = RC_MAP_XBOX_360`. Module lifecycle is `init_rc_map` calling `rc_map_register()` and `exit_rc_map` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_XBOX_360`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is keycode-to-scancode literal order. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_XBOX_360`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_RC6_MCE` format. Source comments preserve device-specific labels/quirks such as "Display"; "DVD Menu"; "Title"; TV key doesn't light the IR LED; "100".

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_XBOX_360` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_RC6_MCE`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-xbox-360.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-xbox-dvd.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-xbox-dvd.c

Purpose: registers the `RC_MAP_XBOX_DVD` rc-core keytable for the Xbox DVD remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table xbox_dvd[]` with 27 mappings (0xa0b -> KEY_OK; 0xaf7 -> KEY_MENU). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(xbox_dvd)`, `.rc_proto = RC_PROTO_XBOX_DVD`, and `.name = RC_MAP_XBOX_DVD`. Module lifecycle is `init_rc_map` calling `rc_map_register()` and `exit_rc_map` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_XBOX_DVD`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_XBOX_DVD`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_XBOX_DVD` format. Source comments preserve device-specific labels/quirks such as based on lircd.conf.xbox.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_XBOX_DVD` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_XBOX_DVD`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-xbox-dvd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-zx-irdec.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-zx-irdec.c

Purpose: registers the `RC_MAP_ZX_IRDEC` rc-core keytable for the zx-irdec remote controller keytable. The file is data-oriented: it binds remote scan codes to Linux input `KEY_*` codes so rc-core can translate decoded IR protocol values into input events for the matching receiver or board driver.

Important APIs and types: the central object is `static struct rc_map_table zx_irdec_table[]` with 40 mappings (0x01 -> KEY_NUMERIC_1; 0x40 -> KEY_POWER). `static struct rc_map_list` supplies `.scan`, `.size = ARRAY_SIZE(zx_irdec_table)`, `.rc_proto = RC_PROTO_NEC`, and `.name = RC_MAP_ZX_IRDEC`. Module lifecycle is `init_rc_map_zx_irdec` calling `rc_map_register()` and `exit_rc_map_zx_irdec` calling `rc_map_unregister()`. The only external headers are `<media/rc-map.h>` for rc-core table declarations and keymap names, and `<linux/module.h>` for module metadata.

Control flow: module insertion registers the static map list with rc-core; lookup is then performed by the rc-core/input stack when a receiver selects `RC_MAP_ZX_IRDEC`. Module removal unregisters the same map list. There is no runtime parsing, allocation, IRQ handling, or direct hardware access in this file.

State and persistence: all state is immutable static table data plus the registration record held by rc-core while the module is loaded. The table literal order is scancode-to-keycode. Duplicate key targets: none; duplicate scan codes: none. Duplicate key targets are acceptable when multiple remote buttons intentionally emit the same Linux input semantic, but duplicate scan codes would make lookup ambiguous.

Dependencies and integration points: depends on rc-core keymap registration and Linux input keycode definitions. It is consumed indirectly by receiver drivers, board definitions, device tree `linux,rc-map-name` properties, or default map selection that names `RC_MAP_ZX_IRDEC`. Protocol correctness depends on the upstream decoder delivering scan codes in `RC_PROTO_NEC` format. Source comments preserve device-specific labels/quirks such as Input method; Application; Location.

Risks: because this file is pure table data, the main risks are incorrect protocol selection, mistyped scan codes, mismatched key semantics, and legacy maps using `RC_PROTO_UNKNOWN`, which leaves protocol handling to the receiver/decoder path. Changing values is user-visible because key names affect applications, media center bindings, and LIRC/scancode mode output. For modules with repeated key targets, tests should verify that the repetition reflects remote labeling rather than accidental copy/paste.

Test signals: build the keymap module, load/unload it, confirm `rc_map_register()` succeeds, select `RC_MAP_ZX_IRDEC` on a compatible rc-core device, and use `ir-keytable -t` or evtest to verify representative buttons against the table. Regression coverage should include protocol-specific decode for `RC_PROTO_NEC`, numeric keys, navigation keys, power/mute/volume, and any device-specific or commented buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-zx-irdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/lirc_dev.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/lirc_dev.c

Purpose: implements the rc-core LIRC character-device bridge. It creates `/dev/lircN` devices for registered `struct rc_dev` instances, delivers raw pulse/space samples and decoded `struct lirc_scancode` records to userspace, accepts LIRC transmit writes, and exposes LIRC ioctl feature/mode/configuration controls.

Important APIs and types: exported/event entry points are `lirc_raw_event()`, `lirc_scancode_event()`, `lirc_register()`, `lirc_unregister()`, `lirc_dev_init()`, `lirc_dev_exit()`, and `rc_dev_get_from_fd()`. The file operations table `lirc_fops` binds `lirc_open`, `lirc_close`, `lirc_read`, `lirc_transmit`, `lirc_ioctl`, and `lirc_poll`. Per-open state is `struct lirc_fh`, which owns raw and scancode kfifos plus receive/send mode fields; device-wide state lives in `struct rc_dev` fields such as `lirc_cdev`, `lirc_dev`, `lirc_fh`, `lirc_fh_lock`, timeout/carrier callbacks, and `tx_ir`.

Control flow: `lirc_dev_init()` registers the `lirc` class and allocates a chrdev region. `lirc_register()` allocates a minor with `ida_alloc_max()`, initializes the embedded device and cdev, initializes the open-file list and spinlock, and publishes the character device. `lirc_open()` validates registration, allocates per-file FIFOs according to driver type, calls `rc_open()`, and links the file handle into the device list. Receive flow enters through `lirc_raw_event()` or `lirc_scancode_event()`, converts rc-core events into LIRC samples or timestamped scancodes, runs BPF for raw samples, enqueues to every open file handle, and wakes poll waiters. Reads block or return `-EAGAIN` until the selected FIFO has data, then copy records to userspace under the rc device mutex. TX flow validates pulse-array or scancode-mode writes, optionally encodes a scancode with `ir_raw_encode_scancode()`, applies carrier hints, calls the hardware `tx_ir()` callback, and sleeps until the requested waveform duration has elapsed. Ioctl flow reports capabilities and forwards carrier, timeout, duty-cycle, transmitter-mask, wideband, and carrier-report settings to optional rc-core callbacks.

State and persistence: persistent kernel state is limited to allocated minors and currently open `struct lirc_fh` instances. Each open file has independent receive/send modes and independent raw/scancode FIFOs, so consumers do not drain each other. `dev->gap_start` preserves inter-frame gap timing for backwards-compatible LIRC raw streams. The code uses the rc device mutex for configuration and reads, a spinlock for file-handle list/FIFO event delivery, wait queues for blocking reads and poll, and device references to keep `struct rc_dev` alive while files are open.

Dependencies and integration points: depends on rc-core internals from `rc-core-priv.h`, UAPI definitions in `<uapi/linux/lirc.h>`, Linux cdev/device/IDA/kfifo/wait/poll APIs, and raw IR encoder helpers. It is the userspace ABI surface for LIRC applications, `ir-keytable`, BPF LIRC hooks, and any rc-core driver advertising raw RX, scancode RX, or TX callbacks.

Risks: ABI behavior is compatibility-sensitive; changes to sample encoding, gap insertion, blocking semantics, or ioctl return codes can break existing LIRC userspace. FIFO writes drop samples silently when full except for the raw overflow marker path. TX scancode mode is limited to encodable 32-bit protocols and rejects invalid scancode/protocol combinations. `LIRC_SET_REC_CARRIER_RANGE` stores only a low bound in the file handle and applies it when `LIRC_SET_REC_CARRIER` later supplies the high bound. The transmit path trusts driver callbacks for actual waveform transmission after validating aggregate duration against `IR_MAX_DURATION`.

Test signals: compile with rc-core/LIRC enabled, create raw RX, scancode RX, and TX-capable rc devices, open multiple `/dev/lircN` handles simultaneously, verify poll/read behavior in MODE2 and SCANCODE modes, exercise all feature ioctls against devices with and without optional callbacks, validate TX pulse and scancode writes including invalid sizes and nonblocking reads, confirm hot-unplug wakes waiters with `EPOLLHUP|EPOLLERR`, and run LIRC/BPF userspace smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/lirc_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/mceusb.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/mceusb.c

Purpose: drives USB Windows Media Center/eHome-compatible infrared transceivers. It matches many vendor/product IDs, initializes model-specific MCE devices, parses inbound command and IR data packets into rc-core raw events, exposes transmit, carrier, timeout, wideband receiver, and carrier-report operations, and handles USB endpoint recovery.

Important APIs and types: module registration uses `module_usb_driver(mceusb_dev_driver)` with `mceusb_dev_probe`, `mceusb_dev_disconnect`, suspend/resume hooks, and `mceusb_dev_table`. Hardware variation is described by `enum mceusb_model_type` and `struct mceusb_model`. Runtime state is `struct mceusb_dev`, containing the rc device, USB device/interface/endpoints/URBs/DMA buffer, packet parser state (`CMD_HEADER`, `SUBCMD`, `CMD_DATA`, `PARSE_IRDATA`), model flags, TX carrier/mask, emulator version, port counts, active receiver state, carrier-measurement accumulators, and deferred error work.

Control flow: probe filters multifunction interfaces, discovers bulk or interrupt IN/OUT endpoints, allocates coherent input buffering and an input URB, initializes model flags, registers an `RC_DRIVER_IR_RAW` rc device, submits the receive URB, queries emulator version, runs generation-specific initialization, queries device parameters, flashes the LED when supported, sets the default TX mask, stores interface data, and enables USB wake. Incoming URBs call `mceusb_dev_recv()`, which dispatches successful buffers to `mceusb_process_ir_data()` and resubmits. The parser walks MCE command headers and IR data packets, handles complete command responses with `mceusb_handle_command()`, converts 50 us pulse/space symbols to `struct ir_raw_event`, emits timeout events on IR trailers, and calls `ir_raw_event_handle()` when useful data was queued. TX calls flow from rc-core into `mceusb_tx_ir()`, which selects TX ports, converts pulse/space durations into MCE packet bytes with headers/trailer and long-duration splitting, and sends buffers synchronously through `mce_write()`. Endpoint stalls schedule `mceusb_deferred_kevent()` to clear halts or queue a USB reset in process context.

State and persistence: state is per USB interface and volatile. `ir->parser_state`, `cmd`, and `rem` preserve packet parsing across URB boundaries for IR data, while command responses spanning URBs are rejected/reset. `need_reset` causes the next command path to send `DEVICE_RESUME`. Carrier measurement tracks pulse-on time and pulse count between frames. TX mask and carrier are cached in the driver. Suspend kills the receive URB and resume resubmits it; disconnect cancels deferred work, unregisters rc-core, kills/frees URB and coherent buffer, and frees the driver state.

Dependencies and integration points: depends on Linux USB core, workqueues, rc-core raw IR support, USB input ID helpers, and numerous rc-map constants. It integrates with rc-core through `rc_register_device()`, `tx_ir`, `s_tx_mask`, `s_tx_carrier`, `s_timeout`, `s_wideband_receiver`, and `s_carrier_report`. Default keymaps are selected by vendor/model, commonly `RC_MAP_RC6_MCE`, with Hauppauge, Pinnacle/PCTV, TiVo, Astrometa, and other overrides.

Risks: the protocol parser is byte-stateful and must tolerate partial IR data while discarding partial command responses. USB write operations allocate a URB per command and block up to `USB_TX_TIMEOUT`; repeated commands during probe and TX can be slow on failing hardware. Model flags encode many device quirks, so incorrect `driver_info` can invert TX masks, expose missing TX, or enable inaccurate carrier reporting. The receive buffer has finite hardware packet capacity and long IR messages can be truncated by the device. Error recovery must avoid doing clear-halt/reset operations in interrupt context and can temporarily drop receive data while recovering.

Test signals: build with USB and rc-core, match representative devices from each model class, verify endpoint discovery for bulk and interrupt endpoints, test probe/disconnect/suspend/resume, receive RC6 MCE and other raw protocols through `ir-keytable`, transmit long and short pulse arrays through LIRC, set TX carrier and mask, enable wideband and carrier-report modes, inject/stimulate TX/RX stalls to exercise deferred recovery, and confirm no URB/DMA leaks under repeated hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/mceusb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/meson-ir-tx.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/meson-ir-tx.c

Purpose: implements the Amlogic Meson IR blaster transmitter as an rc-core raw-TX platform driver for `amlogic,meson-g12a-ir-tx` devices.

Important APIs and types: `struct meson_irtx` stores the MMIO base, current encoded TX buffer/head/length, carrier, duty cycle, spinlock, completion, and modulator clock rate. Probe entry is `meson_irtx_probe()`. rc-core callbacks are `meson_irtx_transmit()`, `meson_irtx_set_carrier()`, and `meson_irtx_set_duty_cycle()`. Hardware helpers include `meson_irtx_setup()`, `meson_irtx_set_mod()`, `meson_irtx_prepare_pulse()`, `meson_irtx_prepare_space()`, and FIFO draining through `meson_irtx_send_buffer()`.

Control flow: probe maps registers, gets the IRQ, initializes defaults and synchronization, chooses the modulator clock from the `xtal` clock or fallback 1 MHz mode, programs the transmitter, requests the FIFO-threshold IRQ, allocates an `RC_DRIVER_IR_RAW_TX` device, and registers it with devm rc-core. Transmit validates each pulse/space duration against hardware timebase limits, allocates a u32 hardware command buffer, encodes pulses with carrier modulation and spaces with the smallest usable timebase, loads the first FIFO batch under lock, waits for IRQ-driven completion up to `IR_MAX_DURATION`, then frees the buffer and clears state.

State and persistence: TX state is transient and protected by `ir->lock`; `buf`, `buf_len`, and `buf_head` describe the active transmission until completion or timeout. Carrier and duty-cycle settings persist in the driver structure and hardware modulator registers while the platform device is active. The completion object serializes caller wait against FIFO-threshold interrupts.

Dependencies and integration points: depends on platform device resources, OF match data, MMIO accessors, clk framework, IRQs, completions, spinlocks, and rc-core raw-TX APIs. Userspace reaches it through LIRC/rc-core transmit interfaces, including carrier and duty-cycle controls.

Risks: only one active transmission is represented in `struct meson_irtx`; concurrent callers rely on upper rc-core serialization. Duration validation rejects values that cannot fit hardware delay fields, but rounding can still alter exact waveform timing. The timeout is based on `IR_MAX_DURATION`, not the exact waveform length. Clock acquisition enables `xtal` but uses devm lifetime without an explicit disable in this file. IRQ handling assumes FIFO threshold interrupts continue until the buffer is drained.

Test signals: device-tree probe on compatible Meson hardware, rc-core registration as TX-only, carrier and duty-cycle setting, short and long transmit waveform validation, FIFO interrupt completion, timeout handling when IRQs do not arrive, and waveform inspection with an IR receiver or oscilloscope.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/meson-ir-tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/meson-ir.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/meson-ir.c

Purpose: implements Amlogic Meson IR receiver support. Older Meson variants run in raw edge-capture mode for software decoding; Meson S4 can use the controller hardware decoder for NEC scancodes.

Important APIs and types: `struct meson_ir` stores match parameters, a regmap, rc device, and spinlock. `struct meson_ir_param` selects hardware-decoder support and register range. `struct meson_ir_protocol` describes timing windows and decoder options; this snapshot defines NEC timing in `protocol_timings`. Key functions are `meson_ir_probe()`, `meson_ir_irq()`, `meson_ir_sw_decoder_init()`, `meson_ir_hw_decoder_init()`, `meson_ir_nec_handler()`, remove/shutdown, and PM suspend/resume.

Control flow: probe allocates state, gets OF match data, maps registers through regmap, obtains the IRQ, allocates either an `RC_DRIVER_IR_RAW` or `RC_DRIVER_SCANCODE` device, assigns allowed protocols and optional `change_protocol`, reads `linux,rc-map-name`, registers rc-core, initializes raw mode immediately when needed, and requests the IRQ. IRQ handling reads status under spinlock; raw mode converts pulse level and `TIME_IV` duration into raw events at 10 us resolution, while scancode mode checks valid-frame status and dispatches the hardware NEC handler. Hardware decoder initialization programs base time, filters, mode, bit order, repeat behavior, frame length, leader/bit timing windows, and enables the decoder. Shutdown switches the controller back to NEC/hardware timing to support bootloader wake behavior.

State and persistence: hardware register configuration persists while the platform device remains powered. Runtime software state is small and devm-managed. The spinlock serializes IRQ-time register access with init, suspend, remove, and shutdown reconfiguration. On resume, the driver reinitializes either hardware or software decoder mode based on match data.

Dependencies and integration points: depends on OF platform matching for `amlogic,meson6-ir`, `amlogic,meson8b-ir`, `amlogic,meson-gxbb-ir`, and `amlogic,meson-s4-ir`, Linux regmap/MMIO, IRQs, bitfield helpers, and rc-core raw/scancode APIs. Board/device-tree integration can select the keymap through `linux,rc-map-name`; otherwise `RC_MAP_EMPTY` is used.

Risks: hardware decoding currently supports only NEC, so enabling other protocols on S4 requires new timing entries and handler logic. Raw duration resolution and hardware timing windows are hard-coded. The IRQ handler returns handled without explicit status clearing beyond hardware read side effects, so behavior depends on the controller register semantics. Shutdown intentionally changes mode for wake, which can surprise low-level debugging. Incorrect device-tree compatible selection can choose the wrong register map or decoder mode.

Test signals: boot on each supported compatible, verify raw pulse capture and software decoding on Meson6/8b/GXBB, verify NEC scancode and repeat handling on Meson S4, test `linux,rc-map-name` selection, suspend/resume reinitialization, remove/shutdown register behavior, and protocol switching through rc-core on hardware-decoder devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/meson-ir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/mtk-cir.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/mtk-cir.c

Purpose: implements the MediaTek MT7622/MT7623 consumer IR receiver as an rc-core raw receiver. It programs sampling periods and interrupt thresholds, reads captured pulse-width registers, and feeds software decoders with raw events.

Important APIs and types: SoC differences are modeled by `struct mtk_ir_data`, register-offset arrays, and field descriptors. `struct mtk_ir` stores device, rc device, MMIO base, IRQ, clocks, and SoC data. Key functions are `mtk_ir_probe()`, `mtk_ir_irq()`, `mtk_ir_remove()`, register helpers (`mtk_w32_mask`, `mtk_w32`, `mtk_r32`), and period calculation in `mtk_chk_period()`.

Control flow: probe gets the IR and optional bus clocks, maps registers, allocates an `RC_DRIVER_IR_RAW` device, applies keymap and input metadata, registers rc-core, gets the IRQ, enables clocks, disables IR interrupts while configuring, requests the IRQ, writes software and hardware sampling periods, sets de-glitch count, enables PWM/IR and OK-count completion, then enables interrupts. On IRQ, the driver reads 17 capture registers, decodes four one-byte pulse/space widths from each, alternates pulse state, scales durations by the sample period, stores raw events, appends a trailing long space if the hardware capture did not end cleanly, runs `ir_raw_event_handle()`, restarts the controller, and clears interrupt status. Remove disables interrupts, synchronizes the IRQ, and disables clocks.

State and persistence: runtime state is devm-managed except for enabled clocks and hardware registers, which are undone in remove. Capture state does not persist across interrupts; each IRQ processes the fixed hardware register bank. The rc device timeout is set to the maximum one-byte sample span.

Dependencies and integration points: depends on OF compatibles `mediatek,mt7623-cir` and `mediatek,mt7622-cir`, clk framework, platform MMIO resources, IRQs, reset-capable hardware state through register writes, and rc-core raw decoders. Device tree may provide `linux,rc-map-name`; otherwise `RC_MAP_EMPTY` is used.

Risks: hardware stores at most 68 pulse/space bytes, so longer frames lose trailing data; the driver mitigates with a trailing long space but cannot recover missing edges. The IRQ parser currently stores all bytes including zero-width tail bytes before relying on decoder filters. Sample period math depends on accurate clock rates and SoC divisor data. Error path after enabling the first clock must disable it if bus-clock enable fails, which this file handles, but runtime PM is not implemented.

Test signals: probe both MT7622 and MT7623 compatibles, validate clock fallback for old device trees without `bus`, measure sample period, receive NEC/RC5/RC6 and long frames through software decoders, exercise overflow/truncation behavior with long captures, remove while IRQs are active, and run suspend-style clock/reset tests at the platform level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/mtk-cir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/nuvoton-cir.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/nuvoton-cir.c

Purpose: drives Nuvoton/Winbond W83667HG, NCT6775F, NCT6776F, and NCT6779D CIR logical devices discovered through PNP. It exposes raw IR receive through rc-core, supports wakeup pattern programming, and configures the companion CIR wake logical device for IR power-on.

Important APIs and types: runtime state is `struct nvt_dev` from `nuvoton-cir.h`, containing the rc device, spinlock, RX buffer, Super-I/O config ports, CIR and wake I/O bases, IRQ, chip identity, and carrier field. The PNP driver uses `nvt_probe`, `nvt_remove`, `nvt_suspend`, `nvt_resume`, and `nvt_shutdown`. Hardware helpers cover extended-function-mode access (`nvt_efm_enable/disable`, `nvt_cr_read/write`), logical-device setup, CIR/CIR-wake register access, FIFO clearing, wake programming, and debug register dumps. rc-core callbacks are `nvt_open`, `nvt_close`, and `nvt_ir_raw_set_wakeup_filter`; sysfs exposes `wakeup_data`.

Control flow: probe allocates state and an `RC_DRIVER_IR_RAW` rc device, activates and validates PNP I/O/IRQ resources, initializes config-port defaults, detects the Super-I/O chip, configures CIR and CIR-wake logical devices in EFM mode, initializes their registers/FIFOs, fills rc-core metadata and wakeup capabilities, registers rc-core, requests I/O regions and a shared IRQ, creates the wakeup sysfs file, and enables device wake. Opening the rc device enables the CIR logical device, TX/RX hardware bits, clears interrupts, and enables RX trigger/packet-end/overrun IRQs; closing disables interrupts, hardware, FIFOs, and the logical device. IRQ handling reads status and enabled masks under spinlock, rejects unrelated shared interrupts, acknowledges status, handles FIFO overrun with rc-core overflow, or reads RX FIFO bytes into the local buffer and publishes raw events. Wake filter programming encodes a selected rc scancode into raw events, converts durations to 50 us wake FIFO bytes, applies a tolerance, and writes the CIR wake FIFO. Suspend/remove/shutdown disable active CIR as needed and enable CIR wake.

State and persistence: device configuration persists in Super-I/O logical-device registers and CIR/CIR-wake I/O registers. Software RX state is `nvt->buf` plus `pkts`, reset after each FIFO drain or overrun. Wake samples persist in the CIR wake FIFO and are visible/editable through the `wakeup_data` sysfs attribute. The spinlock protects CIR register and buffer access in IRQ and configuration paths; rc-core's device mutex is used around user-count checks during suspend/resume.

Dependencies and integration points: depends on PNP IDs `WEC0530` and `NTN0530`, inb/outb I/O port access, shared IRQs, rc-core raw decoder and wakeup-encoder support, Linux sysfs attributes, and constants from `nuvoton-cir.h`. It integrates with input as a host-bus RC6 MCE default remote (`RC_MAP_RC6_MCE`) and with system power management through `device_init_wakeup()` and CIR wake logical-device programming.

Risks: Super-I/O configuration uses global I/O config ports and must acquire the muxed region; failures or alternate EFER ports can prevent detection. Unknown compatible chips are allowed with a warning, which may expose register differences. The RX FIFO and local buffer are small (`RX_BUF_LEN` 32), so overrun drops data and reports overflow. Wake filter encoding truncates/splits durations into a 67-byte wake FIFO and intentionally skips the final small value for tolerance, so not every protocol/scancode will make a robust wake pattern. The shared IRQ path must distinguish unrelated interrupts using status/enabled masks. Several sample-period and trigger-level settings are compile-time constants.

Test signals: boot on supported and unknown Nuvoton chips, verify PNP resource activation, open/close rc device, receive raw events and decode RC6 MCE, provoke FIFO overrun, inspect `wakeup_data`, program wake filters for supported protocols, suspend/resume and power-on by IR, unload/reload with shared IRQs, and test debug register dumps under the `debug` module parameter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/nuvoton-cir.c -->
