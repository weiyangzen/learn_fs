# sources/distributed-fs/ceph-client/drivers/regulator/arizona-micsupp.c

Purpose: provides the microphone supply regulator (`MICVDD`) for Arizona and Madera codec families, including charge-pump bypass and DAPM pin synchronization.

Important APIs/types/functions: `struct arizona_micsupp` stores regulator, regmap, DAPM pointer, descriptor, default init data, and a work item. `arizona_micsupp_enable()`, `disable()`, and `set_bypass()` wrap regmap regulator ops and schedule `arizona_micsupp_check_cp()`, which forces or disables the ASoC DAPM `MICSUPP` pin based on charge-pump state.

Control flow: platform probe chooses normal or extended voltage range descriptors by codec type, fills default constraints, optionally parses a `micvdd` child node, clears bypass to default regulated mode, registers the regulator, and stores driver data. Madera uses the extended descriptor with different register definitions and supply name.

State and persistence: state is devm-managed driver data plus pending work. Hardware state lives in codec regmap enable, bypass, and voltage-selector bits. DAPM state is updated asynchronously after successful regulator state changes.

Dependencies and integration: integrates regulator core, Arizona/Madera MFDs, ASoC DAPM, OF/platform init data, and workqueues. It assumes the parent codec provides a stable DAPM context pointer.

Risks and test signals: asynchronous DAPM work can race driver removal because there is no explicit cancel path. `regmap_update_bits()` clearing bypass during init is not checked for errors. Tests should cover enable/disable/bypass DAPM transitions, null DAPM pointer, normal versus extended ranges, Madera register mapping, and regulator registration failure.
