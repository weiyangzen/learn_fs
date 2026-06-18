# Research: subset-b-001435

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_translate_dce110.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_translate_dce110.c

Purpose: DCE 11.0 GPIO translator that maps raw DC GPIO register offsets and bit masks to DAL `enum gpio_id` plus enum index values, and maps those logical ids back to register metadata in `struct gpio_pin_info`. Important APIs are the static `offset_to_id`, static `id_to_offset`, the `hw_translate_funcs` table, and `dal_hw_translate_dce110_init`. Control flow is table-driven by `switch` statements over DCE 11.0 `mmDC_GPIO_*` offsets and masks. DDC offsets only return `en`, because DDC creation later chooses data or clock ids directly. State is limited to installing `tr->funcs`; no registers are read or written. Dependencies are `dm_services.h`, `gpio_types.h`, `hw_translate.h`, and DCE 11.0 register headers. Integration is through `dal_hw_translate_init` and `gpio_service` create/open paths. Risks are stale masks, unsupported GPIO pad translation, assertion-only failure handling, and assumptions that offset/mask/en numbering matches factory pin counts. Tests should cover HPD1-6, DDC1-6, VGA, I2C pad, generic A-G, sync A, GSL, invalid masks, and round trips through `dal_gpio_get_pin_info`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_translate_dce110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_translate_dce110.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_translate_dce110.h

Purpose: Public DCE 11.0 translator declaration. Important API is `dal_hw_translate_dce110_init(struct hw_translate *tr)`, with `struct hw_translate` forward-declared to avoid exposing the implementation layout. There is no executable control flow and no state except what the implementation writes through the pointer. Dependencies are compile-time only: callers must include a compatible definition of `struct hw_translate` before dereferencing it. Integration is through the common `hw_translate.c` generation dispatcher. Risks are signature drift against the `.c` file, missing include-order coverage, and callers assuming this header defines the translator structure. Test signals are kernel build/link coverage for DCE 10/11 display configurations and any GPIO service tests that instantiate a DCE 11.0 service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_translate_dce110.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c

Purpose: DCE 12.0 GPIO hardware factory that binds DDC and HPD pin objects to Vega10/SOC15 register definitions. Important APIs are `dal_hw_factory_dce120_init`, static `define_ddc_registers`, static `define_hpd_registers`, DDC/HPD register arrays, shift/mask tables, and the `hw_factory_funcs` vtable. Control flow is simple construction: the init routine fills per-id pin counts and function pointers; `gpio_service_open` later calls the define helpers to attach `ddc_registers` or `hpd_registers` to a concrete pin. State is all in the caller-owned `struct hw_factory` and per-pin `hw_ddc`/`hw_hpd` fields; there is no persistence. Dependencies are DCE 12.0 offset/sh-mask headers, SOC15/Vega10 base macros, `hw_ddc`, `hw_hpd`, `hpd_regs.h`, and `ddc_regs.h`. Integration is through `dal_hw_factory_init` for DCE 12.0/12.1. Risks include duplicate `SF_HPD` macro definition, array indexing by unchecked `en`, no generic pin implementation despite a nonzero generic pin count, and ASIC-cap TODOs. Tests should validate HPD0-5, DDC1-6, VGA, I2C pad register attachment, build coverage, and failed opens on unsupported generic paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.h

Purpose: DCE 12.0 factory declaration header. Important API is `dal_hw_factory_dce120_init(struct hw_factory *factory)`, used by the common factory dispatcher to install DCE 12.0 register tables and function pointers. The header has no control flow, persistence, or runtime state. It depends on callers having a visible `struct hw_factory` declaration. Integration points are `hw_factory.c` cases for `DCE_VERSION_12_0` and `DCE_VERSION_12_1`. Risks are signature drift and include-order assumptions. Tests are compile/link coverage for DCE 12.x builds and service creation tests that force the dispatcher through this init function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c

Purpose: DCE 12.0 translator for SOC15/Vega10 register-addressed GPIO blocks. Important APIs are `offset_to_id`, `id_to_offset`, the local `REG`/`BASE` address macros, the function table, and `dal_hw_translate_dce120_init`. Control flow mirrors DCE 11 but uses base-index-expanded `REG(DC_GPIO_*)` addresses. It recognizes generic A-G, HPD1-6, sync A, GSL, DDC1-6, VGA, and I2C pad, and rejects power-sequence, pad-strength, debug, VIP, and unsupported sync B ids. State is only `tr->funcs`; `id_to_offset` fills `offset`, `offset_y`, `offset_en`, `offset_mask`, and matching masks in caller storage. Dependencies are DCE 12.0 offset/sh-mask, SOC15/Vega10 IP offsets, `gpio_types`, and `hw_translate`. Integration is with `gpio_service` creation and pin-info queries. Risks are bad base expansion, no GPIO pad support despite factory count, DDC returning no id in `offset_to_id`, and array/count mismatches. Tests should round-trip each supported id, exercise invalid masks, and compare generated offsets against register headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.h

Purpose: DCE 12.0 translator declaration. Important API is `dal_hw_translate_dce120_init(struct hw_translate *tr)`. The include guard and forward declaration keep the header narrow. It has no runtime control flow and persists no state. Dependencies are limited to a compatible `struct hw_translate` declaration in users. Integration is through `dal_hw_translate_init` for DCE 12.0/12.1. Risks are prototype drift and build configurations that include this header before any translator type declaration. Tests are compiler/linker checks plus GPIO service creation on DCE 12.x versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_factory_dce60.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_factory_dce60.c

Purpose: Southern Islands/DCE 6.x GPIO factory, compiled under `CONFIG_DRM_AMD_DC_SI`, that supplies DDC and HPD register tables. Important APIs are `dal_hw_factory_dce60_init`, `define_ddc_registers`, `define_hpd_registers`, DCE6-specific HPD macros, and DDC register arrays for six DDC lines plus VGA and I2C pad. Control flow sets pin counts and the vtable; later service open attaches DDC or HPD register metadata based on `pin->id` and `en`. State is in `factory` and pin objects only. Dependencies are DCE 6.0 register/sh-mask headers, `hw_ddc`, `hw_hpd`, `ddc_regs.h`, and `hpd_regs.h`. Integration is selected by the common factory for DCE 6.0/6.1/6.4. Risks include no generic implementation while generic count is nonzero, `en` indexing without runtime bounds, old ASIC-specific VGA/I2C semantics, and assertion-oriented error paths. Tests should cover SI build gates, DDC/HPD register attachment, DDC VGA/I2C special cases, and failures on unsupported generic opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_factory_dce60.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_factory_dce60.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_factory_dce60.h

Purpose: DCE 6.x factory declaration header. Important API is `dal_hw_factory_dce60_init(struct hw_factory *factory)`. There is no executable control flow or persistence. Dependencies are the forward visibility of `struct hw_factory` from surrounding includes. Integration is through `hw_factory.c` when SI support is enabled. Risks are header inclusion without the common factory type and signature mismatch with the implementation. Test signals are SI-enabled kernel builds and service creation for DCE 6.0, 6.1, and 6.4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_factory_dce60.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_translate_dce60.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_translate_dce60.c

Purpose: DCE 6.x GPIO translator for SI register names. Important APIs are `index_from_vector`, `offset_to_id`, `id_to_offset`, the function table, and `dal_hw_translate_dce60_init`. Control flow decodes generic, HPD, sync A, GSL, GPIOPAD, DDC, VGA, and I2C pad offsets with DCE6 masks; `index_from_vector` converts a one-hot GPIOPAD mask to an enum index. State is only translator function pointer installation and caller-filled `gpio_pin_info`; there is no hardware access. Dependencies are DCE 6.0 and SMU 6.0 register headers plus common GPIO types. Integration is through `gpio_service_create_irq`, generic mux creation, DDC creation, and pin-info lookups. Risks include one-hot mask assumptions for GPIOPAD, `GPIO_GPIO_PAD_MAX` comparison against a mask-derived enum, unsupported power/debug blocks, assertion-only invalid paths, and DDC id omission in `offset_to_id`. Tests should cover GPIOPAD masks, HPD1-6, generic A-G, GSL, sync A, DDC lines, VGA/I2C pad, and invalid multi-bit masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_translate_dce60.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_translate_dce60.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_translate_dce60.h

Purpose: DCE 6.x translator declaration. Important API is `dal_hw_translate_dce60_init(struct hw_translate *tr)`. The header has no runtime behavior and no state. It depends on caller include order for `struct hw_translate`. Integration is via the common translator dispatcher under SI-supported DCE versions. Risks are prototype drift and missing SI build coverage. Tests are compile/link with `CONFIG_DRM_AMD_DC_SI` and GPIO service creation on DCE 6.x.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_translate_dce60.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_factory_dce80.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_factory_dce80.c

Purpose: DCE 8.x GPIO factory for DDC and HPD pins using DCE 8.0 register headers. Important APIs mirror DCE6: `dal_hw_factory_dce80_init`, `define_ddc_registers`, `define_hpd_registers`, HPD register arrays, DDC data/clock arrays, and the `hw_factory_funcs` vtable. Control flow fills pin counts, then attaches register metadata when the service opens DDC or HPD pins. State is in caller-owned factory and pin structs only. Dependencies are DCE 8.0 register/sh-mask headers and common DDC/HPD helpers. Integration is selected for DCE 8.0, 8.1, and 8.3. Risks are unsupported generic function pointers despite generic count, unchecked `en` indexing, and reliance on old DCE register layouts matching `ddc_regs.h` and `hpd_regs.h`. Tests should verify DDC1-6/VGA/I2C and HPD1-6 register table selection and generic open failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_factory_dce80.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_factory_dce80.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_factory_dce80.h

Purpose: DCE 8.x factory declaration. Important API is `dal_hw_factory_dce80_init(struct hw_factory *factory)`. It contains no executable control flow and stores no state. Integration is through `hw_factory.c` for DCE 8.x versions. Dependencies are include-order visibility of `struct hw_factory`. Risks are signature drift and missing build coverage for older DCE targets. Tests are compiler/link checks and GPIO service construction on DCE 8.0/8.1/8.3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_factory_dce80.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_translate_dce80.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_translate_dce80.c

Purpose: DCE 8.x GPIO translator using DCE 8.0 and SMU 7 register names. Important APIs are `index_from_vector`, `offset_to_id`, `id_to_offset`, `funcs`, and `dal_hw_translate_dce80_init`. Control flow is equivalent to DCE6 with DCE8 masks: it recognizes generic A-G, HPD1-6, sync A, GSL, GPIOPAD, DDC1-6, VGA, and I2C pad. State is only function-pointer installation plus caller output in `gpio_pin_info`. Dependencies are DCE 8.0 sh/mask headers, SMU 7.0.1 offsets, and common GPIO translation types. Integration is service creation, DDC construction, IRQ source creation, and pin-info lookup. Risks include one-hot GPIOPAD assumptions, DDC `offset_to_id` not setting `id`, unsupported power/pad/debug blocks, and old mask constants drifting from register headers. Tests should round-trip every supported DCE8 id/en pair and validate invalid masks return false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_translate_dce80.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_translate_dce80.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_translate_dce80.h

Purpose: DCE 8.x translator declaration. Important API is `dal_hw_translate_dce80_init(struct hw_translate *tr)`. There is no runtime state or control flow. Dependencies are a visible `struct hw_translate` declaration in including translation units. Integration is through the common translator dispatcher for DCE 8.x. Risks are prototype mismatch and stale include guards. Tests are build/link coverage plus service creation under DCE 8.x versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_translate_dce80.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.c

Purpose: DCN 1.0 GPIO factory that extends the DCE-style DDC/HPD setup with generic mux pin support. Important APIs are `dal_hw_factory_dcn10_init`, `define_ddc_registers`, `define_hpd_registers`, `define_generic_registers`, register arrays for DDC/HPD/generic muxes, and the factory vtable. Control flow expands SOC15 DCN 1.0 register bases, fills DDC1-6/VGA/I2C and HPD0-5 tables, builds generic A/B mux register tables, and installs init/get/define functions for DDC, HPD, and generic pins. State is caller-owned factory and pin register pointers. Dependencies are DCN 1.0 offset/sh-mask headers, Vega10 IP offsets, `ddc_regs.h`, `hpd_regs.h`, `generic_regs.h`, and pin constructors. Integration is selected for DCN 1.0/1.01. Risks include generic pin count 7 while only two generic register table entries exist, unchecked `en` indexing, and old TODO ASIC caps. Tests should open DDC, HPD, and generic mux pins, verify register tables, and exercise invalid generic indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.h

Purpose: DCN 1.0 factory declaration. Important API is `dal_hw_factory_dcn10_init(struct hw_factory *factory)`. The header has no runtime control flow or persistence. It integrates through `hw_factory.c` for DCN 1.0 and 1.01. Dependencies are type visibility for `struct hw_factory`. Risks are signature drift and missing include coverage. Tests are compile/link checks and service creation on DCN 1.0 targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.c

Purpose: DCN 1.0 translator using SOC15 base-expanded DCN 1.0 GPIO offsets. Important APIs are `offset_to_id`, `id_to_offset`, `funcs`, and `dal_hw_translate_dcn10_init`. Control flow maps generic A-G, HPD1-6, sync A, GSL, DDC1-6, VGA, and I2C pad; GPIO pad id translation is not implemented in this DCN path. State is only the translator vtable and caller-filled pin info. Dependencies are DCN 1.0 sh/mask, SOC15/Vega10 offsets, and common GPIO types. Integration is through service DDC creation, IRQ/generic mux creation, and pin-info queries. Risks include mismatch between generic translator support and factory register entries, no GPIOPAD or sync B support, DDC `offset_to_id` leaving `id` untouched, and address-base macro drift. Tests should round-trip supported ids, check unsupported GPIOPAD/sync B cases, and validate offsets against DCN 1.0 register headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.h

Purpose: DCN 1.0 translator declaration. Important API is `dal_hw_translate_dcn10_init(struct hw_translate *tr)`. It has no executable logic or persistence. Integration is via the common translator dispatcher for DCN 1.0/1.01. Dependencies are include-order type visibility. Risks are prototype drift and missing build coverage. Tests are compiler/link checks plus GPIO service creation on DCN 1.0 versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c

Purpose: DCN 2.0 GPIO factory for DDC, HPD, and generic mux pins. Important APIs are `dal_hw_factory_dcn20_init`, DDC/HPD/generic register tables, per-DDC shift/mask arrays using `DDC_MASK_SH_LIST_DCN2`, and the define helpers. Control flow attaches DCN2 DDC registers for DDC1-6 plus VGA fallback, HPD0-5 registers, and generic A/B mux registers. State is caller-owned factory plus pin register/mask pointers. Dependencies are DCN 2.0 register headers, DPCS/PHY AUX fields through `ddc_regs.h`, `generic_regs.h`, and common pin constructors. Integration is selected for `DCN_VERSION_2_0`. Risks include factory pin counts of 8 DDC entries while arrays have DCN lines plus VGA, generic count 4 while only A/B register arrays exist, no sync/GSL pins, and unchecked `en` indexing. Tests should validate DDC AUX/I2C mode fields, HPD filters, generic mux config, VGA dummy behavior, and invalid indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.h

Purpose: DCN 2.0 factory declaration. Important API is `dal_hw_factory_dcn20_init(struct hw_factory *factory)`. There is no runtime control flow or state. Integration is the common factory dispatcher for DCN 2.0. Dependencies are caller-visible `struct hw_factory`. Risks are signature drift and missing DCN2 build coverage. Tests are compile/link and GPIO service construction on DCN 2.0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_translate_dcn20.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_translate_dcn20.c

Purpose: DCN 2.0 GPIO translator. Important APIs are `offset_to_id`, `id_to_offset`, and `dal_hw_translate_dcn20_init`. Control flow decodes generic A-G, HPD1-6, GSL, DDC1-6, and VGA. Sync and I2C pad paths are explicitly absent in comments, and GPIOPAD is not handled. State is limited to the function table and caller-filled pin info. Dependencies are DCN 2.0 offset/sh-mask headers, DCN base macros, and common GPIO translation types. Integration is the GPIO service path for DCN 2.0 DDC creation, HPD IRQ mapping, generic mux setup, and pin-info queries. Risks include translator support for GSL/generic values whose factory counts or register arrays are limited, no sync support despite inherited cases, DDC `offset_to_id` omitting `id`, and unchecked assumptions around DDC6/VGA indices. Tests should round-trip DDC1-6/VGA, HPD1-6, generic masks, and verify unsupported sync/I2C pad/invalid masks fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_translate_dcn20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_translate_dcn20.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_translate_dcn20.h

Purpose: DCN 2.0 translator declaration. Important API is `dal_hw_translate_dcn20_init(struct hw_translate *tr)`. There is no runtime control flow or persistence. Integration is through the common translator dispatcher for DCN 2.0. Dependencies are a visible `struct hw_translate`. Risks are signature drift and missing DCN2 build coverage. Tests are compile/link plus service creation on DCN 2.0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_translate_dcn20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c

Purpose: DCN 2.1 factory variant using DMU/DCN 2.1 register bases and reduced DDC/generic tables. Important APIs are `dal_hw_factory_dcn21_init`, define helpers, DDC1-5 data/clock arrays, HPD0-5 tables, generic A table, and per-line DDC shift/mask arrays. Control flow installs DDC/HPD/generic constructors and register attachment callbacks. State is in the factory and per-pin register pointers. Dependencies are DCN 2.1 offset/sh-mask headers, DMU base macros, `ddc_regs.h`, `hpd_regs.h`, and `generic_regs.h`. Integration covers DCN 2.01 and 2.1 versions in `hw_factory.c`. Risks include factory counts of 8 DDC and 4 generic pins while only DDC1-5 and generic A table entries are present, unchecked `en` indexing, and no sync/GSL factory storage. Tests should verify DDC1-5, HPD1-6, generic A, invalid DDC6/VGA expectations, and AUX/I2C mode register fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.h

Purpose: DCN 2.1 factory declaration. Important API is `dal_hw_factory_dcn21_init(struct hw_factory *factory)`. It has no runtime state. Integration is via the common factory dispatcher for DCN 2.01 and 2.1. Dependencies are type visibility for `struct hw_factory`. Risks are signature drift and stale generation selection. Tests are build/link and GPIO service creation on DCN 2.1 families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c

Purpose: DCN 2.1 translator for DMU-based register offsets. Important APIs are `offset_to_id`, `id_to_offset`, `funcs`, and `dal_hw_translate_dcn21_init`. Control flow maps generic A-G, HPD1-6, GSL masks, DDC1-5, and VGA, while comments mark I2C pad and sync absent. State is only translator vtable and caller-filled pin info. Dependencies are DCN 2.1 register headers and common GPIO types. Integration is used by GPIO service creation for DCN 2.01/2.1. Risks include GSL and generic mappings not matching factory pin counts, no DDC6 mapping, DDC offsets not setting `id`, and unsupported sync/GPIOPAD paths. Tests should cover DDC1-5/VGA, HPD1-6, generic masks, invalid DDC6/I2C pad/sync, and round-trip `id_to_offset` data/clock masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.h

Purpose: DCN 2.1 translator declaration. Important API is `dal_hw_translate_dcn21_init(struct hw_translate *tr)`. There is no executable logic or persistence. Integration is through the common translator dispatcher for DCN 2.01/2.1. Dependencies are caller-visible `struct hw_translate`. Risks are prototype drift and missing target coverage. Tests are build/link plus GPIO service construction on DCN 2.1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c

Purpose: DCN 3.0-family GPIO factory. Important APIs are `dal_hw_factory_dcn30_init`, DDC1-6/VGA register tables, HPD0-5 tables, generic A/B tables, shift/mask arrays, and define helpers. Control flow uses DCN base-expanded register macros to install DDC, HPD, and generic pin support; the common factory selects it for DCN 3.0, 3.01, 3.02, 3.03, 3.1, 3.14, and 3.16. State is the factory vtable and per-pin register pointers. Dependencies are DCN 3.0 register headers, `ddc_regs.h`, `hpd_regs.h`, `generic_regs.h`, and pin constructors. Risks include broad version reuse with TODO ASIC caps, DDC/generic count versus array-size mismatches, unchecked `en`, and no sync/GSL factory support. Tests should verify all selected DCN3 versions instantiate the same tables, DDC AUX/I2C mode fields work, HPD filters program, and invalid DDC/generic indices do not reach register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.h

Purpose: DCN 3.0-family factory declaration. Important API is `dal_hw_factory_dcn30_init(struct hw_factory *factory)`. It has no runtime state. Integration is through `hw_factory.c` for multiple DCN 3.x versions. Dependencies are include-order type visibility. Risks are signature drift and accidental use for a DCN generation with different pin topology. Tests are build/link plus service creation for every version routed to this init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c

Purpose: DCN 3.0 translator for GPIO logical/register mapping. Important APIs are `offset_to_id`, `id_to_offset`, `funcs`, and `dal_hw_translate_dcn30_init`. Control flow recognizes generic A-G, HPD1-6, GSL, DDC1-6, and VGA while excluding I2C pad and sync. State is limited to the installed translator function table and caller-filled pin info. Dependencies are DCN 3.0 offset/sh-mask headers and common GPIO types. Integration covers all DCN 3.x versions mapped to the DCN30 translator. Risks include translator support wider than factory generic tables, no GPIOPAD/sync support, DDC offset decoding not assigning an id, and broad reuse across ASICs with possible topology differences. Tests should round-trip DDC1-6/VGA, HPD1-6, generic masks, invalid I2C/sync/GPIOPAD inputs, and compare offsets with DCN3 headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.h

Purpose: DCN 3.0 translator declaration. Important API is `dal_hw_translate_dcn30_init(struct hw_translate *tr)`. There is no runtime control flow or persistence. Integration is through the common translator dispatcher for DCN 3.0-family versions. Dependencies are caller-visible `struct hw_translate`. Risks are signature drift and insufficient per-version test coverage. Tests are build/link and GPIO service creation for each version routed here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c

Purpose: DCN 3.15 GPIO factory with local DCN base-segment definitions and reduced DDC topology. Important APIs are `dal_hw_factory_dcn315_init`, define helpers, DDC1-5 plus VGA register arrays, HPD0-5, generic A/B, and per-line shift/mask arrays. Control flow installs DDC, HPD, and generic pin handlers for `DCN_VERSION_3_15`. State is factory vtable and per-pin register pointers. Dependencies include DCN 3.1.5 register headers, local segment constants, and common GPIO register macros. Risks include DDC count 8 with only five real DDC lines plus VGA, generic count 4 with two register tables, unchecked `en`, and no sync/GSL factory support. Tests should cover DDC1-5/VGA, HPD1-6, generic A/B, dummy or unsupported DDC6 behavior, and AUX/I2C mode fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.h

Purpose: DCN 3.15 factory declaration. Important API is `dal_hw_factory_dcn315_init(struct hw_factory *factory)`. There is no runtime behavior. Integration is through `hw_factory.c` for `DCN_VERSION_3_15`. Dependencies are type visibility for `struct hw_factory`. Risks are prototype drift and missed DCN 3.15-specific topology tests. Test signals are compile/link and service creation for DCN 3.15.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c

Purpose: DCN 3.15 translator with local base-segment constants. Important APIs are `offset_to_id`, `id_to_offset`, `funcs`, and `dal_hw_translate_dcn315_init`. Control flow maps generic A-G, HPD1-6, GSL, DDC1-5, and VGA; I2C pad and sync are absent. State is only the translator vtable and caller-filled pin metadata. Dependencies are DCN 3.1.5 register headers and common GPIO translation types. Integration is the GPIO service path for DCN 3.15. Risks include DDC masks using DDC1 data/clock masks for all lines, translator/factory count mismatches, no DDC6, and broad generic/GSL cases with no factory support. Tests should round-trip DDC1-5/VGA, HPD1-6, generic masks, invalid DDC6/I2C/sync, and verify base-expanded offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.h

Purpose: DCN 3.15 translator declaration. Important API is `dal_hw_translate_dcn315_init(struct hw_translate *tr)`. It has no runtime state or control flow. Integration is through the common translator dispatcher for DCN 3.15. Dependencies are caller-visible `struct hw_translate`. Risks are prototype drift and missing DCN 3.15 build coverage. Tests are compiler/link and GPIO service creation on DCN 3.15.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c

Purpose: DCN 3.2-family GPIO factory with five HPDs and DDC dummy entries for missing ports. Important APIs are `dal_hw_factory_dcn32_init`, DDC1-5 plus dummy plus VGA register arrays, HPD0-4 tables, generic A/B tables, and define helpers. Control flow installs DDC, HPD, and generic handlers for DCN 3.2, 3.21, 3.5, 3.51, and 3.6. State is factory and per-pin register/mask pointers. Dependencies are DCN 3.2 headers, local segment constants, common GPIO register macros, and pin constructors. Risks include dummy DDC entries that must never be programmed as real hardware, HPD count reduced to five, generic count 4 with two tables, unchecked `en`, and reuse across several later DCN 3.x versions. Tests should verify HPD1-5 only, DDC1-5/VGA, dummy DDC6 behavior, generic mux setup, and all routed versions selecting this factory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.h

Purpose: DCN 3.2-family factory declaration. Important API is `dal_hw_factory_dcn32_init(struct hw_factory *factory)`. The header has no executable behavior. Integration is through common factory cases for DCN 3.2, 3.21, 3.5, 3.51, and 3.6. Dependencies are `struct hw_factory` visibility. Risks are signature drift and per-generation topology differences hidden behind one init. Tests are build/link and service creation for every routed version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c

Purpose: DCN 3.2-family translator. Important APIs are `offset_to_id`, `id_to_offset`, `funcs`, and `dal_hw_translate_dcn32_init`. Control flow maps generic A-F, HPD1-5, GSL, DDC1-5, and VGA. It omits generic G, HPD6, I2C pad, sync, and GPIOPAD support. State is only the installed function table and caller output in `gpio_pin_info`. Dependencies are DCN 3.2 headers and common GPIO types. Integration covers the factory versions routed to DCN32. Risks include cases for GSL despite no GSL pin count, no explicit dummy DDC6 translation even though the factory has a dummy table, reduced HPD/generic topology, and DDC `offset_to_id` not assigning an id. Tests should round-trip supported DDC/HPD/generic values, reject HPD6/DDC6/generic G/sync, and compare base-expanded offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.h

Purpose: DCN 3.2-family translator declaration. Important API is `dal_hw_translate_dcn32_init(struct hw_translate *tr)`. It has no runtime state. Integration is through the common translator dispatcher for DCN 3.2, 3.21, 3.5, 3.51, and 3.6. Dependencies are caller-visible `struct hw_translate`. Risks are signature drift and hidden topology differences among routed versions. Tests are build/link and GPIO service creation for all routed generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_factory_dcn401.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_factory_dcn401.c

Purpose: DCN 4.01 GPIO factory. Important APIs are `dal_hw_factory_dcn401_init`, DDC1-4 plus dummy entries plus VGA register arrays, HPD0-4 tables, generic A/B tables, and define helpers. Control flow uses DCN 4.01 register headers with a local segment base, installs DDC/HPD/generic constructors, and records five HPDs, four generic pins, and 28 GPIO pads. State is factory and pin register pointers only. Dependencies are DCN 4.01 and DPCS 4.0 register headers, `ddc_regs.h`, `hpd_regs.h`, `generic_regs.h`, and common constructors. Integration is selected for `DCN_VERSION_4_01`. Risks include dummy DDC entries for absent ports, unchecked `en`, generic count versus table size, and new-generation register layout churn. Tests should verify DDC1-4/VGA, dummy DDC5/6 handling, HPD1-5, generic mux config, AUX/I2C mode fields, and build coverage against DCN 4.01 headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_factory_dcn401.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_factory_dcn401.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_factory_dcn401.h

Purpose: DCN 4.01 factory declaration. Important API is `dal_hw_factory_dcn401_init(struct hw_factory *factory)`. It has no runtime control flow or persistence. Integration is via the common factory dispatcher for DCN 4.01. Dependencies are type visibility for `struct hw_factory`. Risks are prototype drift and generation-specific register churn. Tests are compile/link and GPIO service construction on DCN 4.01.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_factory_dcn401.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.c

Purpose: DCN 4.01 GPIO translator. Important APIs are `offset_to_id`, `id_to_offset`, `funcs`, and `dal_hw_translate_dcn401_init`. Control flow maps generic A-F, HPD1-5, GSL, DDC1-4, DDC5 in `id_to_offset`, and VGA; comments mark I2C pad and sync absent. State is the translator vtable and caller-filled pin info. Dependencies are DCN 4.01 and DPCS register headers plus common GPIO types. Integration is through DCN 4.01 GPIO service creation. Risks include `id_to_offset` accepting DDC5 while `offset_to_id` does not decode a DDC5 offset, dummy factory entries, GSL cases without GSL pin storage, and unsupported GPIOPAD/sync. Tests should round-trip DDC1-4/VGA, check DDC5 asymmetry, HPD1-5, generic A-F, and invalid HPD6/generic G/sync paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.h

Purpose: DCN 4.01 translator declaration. Important API is `dal_hw_translate_dcn401_init(struct hw_translate *tr)`. It has no runtime state. Integration is through the common translator dispatcher for DCN 4.01. Dependencies are caller-visible `struct hw_translate`. Risks are signature drift and register-generation churn. Tests are build/link and GPIO service creation on DCN 4.01.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c

Purpose: DCN 4.2 GPIO factory for the newer DCN/DPCS register layout. Important APIs are `dal_hw_factory_dcn42_init`, DDC1-5 plus dummy plus VGA register arrays, HPD0-4 tables, zeroed generic tables, and define helpers. Control flow differs from older generations because `DC_GPIO_HPD_*` registers are gone; HPD tables only use interrupt status and toggle filter registers. Generic register structures are intentionally zeroed. State is factory vtable and per-pin register pointers. Dependencies are DCN 4.2.0 and DPCS 4.0 headers, common DDC/HPD/generic macros, and pin constructors. Integration is selected for `DCN_VERSION_4_2`. Risks include zeroed generic register pointers with generic functions still installed, dummy DDC6, reduced HPD count, no GPIO register tuple for HPD sense pins, unchecked `en`, and very new register definitions. Tests should cover HPD interrupt/filter setup, DDC1-5/VGA, dummy DDC6, generic mux no-op/invalid behavior, and DCN 4.2 build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.h

Purpose: DCN 4.2 factory declaration. Important API is `dal_hw_factory_dcn42_init(struct hw_factory *factory)`. It has no runtime control flow or persistence. Integration is through the common factory dispatcher for DCN 4.2. Dependencies are `struct hw_factory` type visibility. Risks are signature drift and new-generation topology assumptions. Tests are build/link and GPIO service creation on DCN 4.2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.c

Purpose: DCN 4.2 translator for the newer HPD/DDC layout. Important APIs are `offset_to_id`, `id_to_offset`, `funcs`, and `dal_hw_translate_dcn42_init`. Control flow maps HPD by HPD interrupt-status offsets rather than GPIO HPD mask bits, ignores the input mask for HPD, and maps DDC1-5 plus VGA. It does not support generic, GSL, sync, GPIOPAD, or I2C pad ids. State is only the translator vtable and caller-filled pin info. Dependencies are DCN 4.2.0 and DPCS 4.0 headers plus common GPIO types. Integration is through DCN 4.2 GPIO service creation and HPD IRQ lookup. Risks include loss of mask discrimination for HPD, no generic translation despite factory generic hooks, DDC6 dummy asymmetry, unsupported I2C pad, and new-register offset drift. Tests should cover HPD1-5 from interrupt-status offsets, DDC1-5/VGA round trips, invalid generic/HPD6/DDC6/sync/I2C cases, and mask-ignored HPD behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.h

Purpose: DCN 4.2 translator declaration. Important APIs are `dal_hw_translate_dcn42_init(struct hw_translate *tr)` and, under `DAL_EMULATION_SUPPORTED`, `dal_emulated_hw_translate_dcn42_init(struct hw_translate *tr)`. The header has no runtime behavior. Integration is through the common translator dispatcher and optional emulation builds. Dependencies are caller-visible `struct hw_translate`. Risks include emulation prototype lacking an implementation in non-emulation objects, signature drift, and missing conditional-build coverage. Tests are compile/link for normal and emulation configurations plus service creation on DCN 4.2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/ddc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/ddc_regs.h

Purpose: Shared DDC register-description macro header. Important types are `struct ddc_registers` and `struct ddc_sh_mask`; important macros include `DDC_GPIO_REG_LIST`, `DDC_REG_LIST`, `DDC_REG_LIST_DCN2`, VGA/I2C variants, `DDC_MASK_SH_LIST`, `DDC_MASK_SH_LIST_DCN2`, and helper initializers such as `ddc_data_regs(id)` and `ddc_data_regs_dcn2(id)`. Control flow is compile-time macro expansion only. State is static data produced in generation factory files: GPIO register tuples, DDC setup register offsets, PHY AUX control offsets, and AUX/I2C field shifts/masks. Dependencies are `gpio_regs.h` and generation-specific `REG`, `SF_DDC`, and register-field macros supplied by includers. Integration is with `hw_ddc.c` and all generation factories. Risks include macro context sensitivity, typo-prone token pasting, DCN2 `ddc_i2c_clk_regs_dcn2` using a DDC-style macro, dummy entries with zero registers, and shift/mask arrays needing exact line order. Tests are compile coverage for every generation factory plus runtime DDC I2C/AUX mode and EDID polling register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/ddc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/generic_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/generic_regs.h

Purpose: Shared generic GPIO mux register macro header. Important types are `struct generic_registers` and `struct generic_sh_mask`; important macros are `GENERIC_GPIO_REG_LIST_ENTRY`, `GENERIC_GPIO_REG_LIST`, `GENERIC_REG_LIST`, and `GENERIC_MASK_SH_LIST`. Control flow is compile-time macro expansion. State is static register/mask tables created by DCN generation factories and consumed by `hw_generic.c`. Dependencies are `gpio_regs.h` and includer-defined `REG`, `SF_GENERIC`, and register-field names. Integration is with generic mux setup through `dal_mux_setup_config` and `hw_generic` set-config. Risks are macro-context fragility, only some generations providing real generic register tables, zeroed DCN4.2 tables, and mismatches between generic enum counts and table length. Tests should build every generation factory and exercise generic mux enable/select writes on generations with real generic registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/generic_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/gpio_base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/gpio_base.c

Purpose: Public GPIO object wrapper that forwards high-level DAL GPIO operations to the service and hardware pin vtable. Important APIs are `dal_gpio_open`, `dal_gpio_open_ex`, `dal_gpio_get_value`, `dal_gpio_set_value`, `dal_gpio_change_mode`, `dal_gpio_set_config`, `dal_gpio_get_pin_info`, `dal_gpio_get_sync_source`, `dal_gpio_get_ddc`, `dal_gpio_get_hpd`, `dal_gpio_get_generic`, and `dal_gpio_close`. Control flow checks open state and null handles, records requested mode before calling `dal_gpio_service_open`, and delegates operations to `gpio->pin->funcs`. State is the mutable `struct gpio`: mode, pin pointer, output state, service pointer, and hardware container. Dependencies are GPIO service, factory/translate types, and `hw_gpio` operations. Integration includes DDC, HPD IRQ, generic mux, sync-source mapping, and higher display services. Risks include assuming `hw_container.ddc` is valid for all gpio types, rollback behavior relying on service close, assertion-only invalid paths, and no locking around mode changes. Tests should cover open/close lifecycle, duplicate open, null pin operations, get/set value, mode changes, config forwarding, pin-info translation, and sync-source mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/gpio_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/gpio_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/gpio_regs.h

Purpose: Common register tuple definition for hardware GPIO pins. Important type is `struct gpio_registers`, which stores register offsets plus masks and shifts for the MASK, A, EN, and Y registers. There is no executable control flow or persistence. Dependencies are only fixed-width integer types available through includers. Integration is embedded in `ddc_registers`, `hpd_registers`, and `generic_registers`, then consumed by `hw_gpio` and specialized pin implementations. Risks are layout assumptions shared across all macro-generated register tables, zeroed dummy tuples, and generations such as DCN4.2 where HPD no longer has a full GPIO tuple. Tests are compile coverage and runtime reads/writes through DDC/generic/HPD pins that validate the tuple fields point at the expected registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/gpio_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/gpio_service.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/gpio_service.c

Purpose: GPIO service lifecycle, allocation, pin busy tracking, and higher-level DDC/IRQ/generic helper creation. Important APIs include `dal_gpio_service_create`, `dal_gpio_service_destroy`, `dal_gpio_service_open`, `dal_gpio_service_close`, lock/unlock helpers, `dal_gpio_service_create_irq`, `dal_gpio_service_create_generic_mux`, DDC create/destroy/open/change-mode/config helpers, IRQ source helpers, and HPD/mux config setup. Control flow creates generation translate and factory objects, allocates one busyness byte array per GPIO id based on factory pin counts, resolves offsets through translator callbacks, constructs GPIO/DDC objects, opens pins through factory vtables, defines registers, calls hardware open, and marks pins busy. State is in `struct gpio_service`: context, translator, factory, and busyness arrays; DDC objects store data/clock pins and hardware info. Dependencies include `dm_services`, GPIO interfaces, `hw_translate`, `hw_factory`, and `hw_gpio`. Integration is central to AMD DC connector detection, DDC/I2C/AUX mode switching, HPD IRQ setup, and generic mux control. Risks include busyness indexing without `en` bounds in several paths, no locking around busyness arrays, factory/translator count mismatch, partial allocation cleanup complexity, and assertion-heavy error handling. Tests should cover service creation failure cleanup, busy/open/close semantics, DDC two-pin rollback, IRQ source mapping, generic mux config, invalid offsets, and all generation factory/translator combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/gpio_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/gpio_service.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/gpio_service.h

Purpose: Internal GPIO service structure and core service operation declarations. Important type is `struct gpio_service`, containing `ctx`, `struct hw_translate`, `struct hw_factory`, and per-id `busyness` arrays. Important APIs are `dal_gpio_service_open`, `dal_gpio_service_close`, `dal_gpio_service_lock`, and `dal_gpio_service_unlock`. There is no executable control flow in the header. State described here is owned by `gpio_service.c`; busyness stores one byte per pin enum. Dependencies are forward declarations for `hw_translate` and `hw_factory`, plus GPIO/DC types supplied by includers. Integration is with `gpio_base.c`, DDC helpers, and service creation/destruction in public GPIO service interfaces. Risks include exposing internals to translation units, busyness array lifetime/size assumptions, and no documented synchronization contract. Tests are compile coverage and runtime open/lock/unlock/close sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/gpio_service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hpd_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hpd_regs.h

Purpose: Shared HPD register macro header. Important types are `struct hpd_registers` and `struct hpd_sh_mask`; important macros include `HPD_GPIO_REG_LIST_ENTRY`, `HPD_GPIO_REG_LIST`, `HPD_REG_LIST`, and `HPD_MASK_SH_LIST`. Control flow is compile-time macro expansion only. State is generated static register and mask tables in generation factory files: common GPIO tuple plus HPD interrupt status and toggle filter control registers. Dependencies are `gpio_regs.h` and includer-defined `REG`, `REGI`, `SF_HPD`, and HPD register-field macros. Integration is with `hw_hpd` and factory define helpers that attach HPD register tables before opening pins or configuring filters. Risks include generation-specific HPD numbering differences, DCN4.2 overriding `HPD_REG_LIST` because GPIO HPD registers are gone, macro context sensitivity, and token-pasted `ONE_MORE_*` legacy numbering. Tests are compile coverage across DCE/DCN factories and HPD filter/sense operations on each generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hpd_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_ddc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_ddc.c

Purpose: Hardware DDC pin specialization on top of `hw_gpio`. Important APIs are `dal_hw_ddc_init`, `dal_hw_ddc_get_pin`, the local `set_config`, destructor/destroy helpers, and the static `hw_gpio_pin_funcs` vtable. Control flow allocates a `struct hw_ddc`, constructs the embedded GPIO pin, and uses `set_config` to switch DDC pads between I2C, AUX, EDID polling, disconnect polling, or disabled polling. State is the `hw_ddc` object: base GPIO state plus generation-attached `ddc_registers`, shifts, and masks. Register writes affect pull-downs, AUX pad mode, optional `DDC_PAD_I2CMODE`, optional `AUX_PAD_RXSEL`, and DDC setup polling fields. Dependencies are `reg_helper.h`, `gpio_regs.h`, `ddc_regs.h`, and generation factory tables. Integration is through `dal_ddc_open`, `dal_ddc_set_config`, and DC connector detection/link AUX logic. Risks include sleeping during detect-mode pad discharge, special VIP/VGA behavior, optional zero registers, config type assumptions, and register-table correctness. Tests should cover I2C/AUX transitions, polling enable/disable, VIP pad paths, dummy zero registers, and open/config rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_ddc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_ddc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_ddc.h

Purpose: Hardware DDC object declaration. Important type is `struct hw_ddc`, which embeds `struct hw_gpio` and stores pointers to `ddc_registers`, shifts, and masks. Important APIs are `dal_hw_ddc_init` and `dal_hw_ddc_get_pin`; important macro is `HW_DDC_FROM_BASE`. There is no executable control flow in the header. State is owned by allocated `hw_ddc` instances and populated by generation factories. Dependencies are `ddc_regs.h` and `hw_gpio` container conventions from includers. Integration is DDC pin construction, service open, and config programming in `hw_ddc.c`. Risks are container-cast misuse, null register pointers before factory define, and generation arrays assigning dummy zero registers. Tests are compile coverage and DDC open/config paths that confirm the embedded base object and register pointers are valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_ddc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_factory.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_factory.c

Purpose: Common factory dispatcher that selects a generation-specific GPIO hardware factory from `enum dce_version`. Important API is `dal_hw_factory_init`. Control flow is a single switch mapping DCE 6.x, 8.x, 10/11.x, 12.x, DCN 1.x, 2.x, 3.x, 4.01, and 4.2 versions to their `dal_hw_factory_*_init` functions; SI cases are conditional on `CONFIG_DRM_AMD_DC_SI`. State mutations occur through the caller's `struct hw_factory`, which receives pin counts and function pointers from the selected implementation. Dependencies are generation factory headers and `gpio_types.h`. Integration is `dal_gpio_service_create`, which calls this after translator initialization and then allocates busyness arrays based on `number_of_pins`. Risks are missing switch cases for new versions, routing a version to a factory with wrong topology, ignoring `dce_environment`, and assertion-only default failure. Tests should instantiate every supported `dce_version`, verify selected pin counts and funcs, and ensure unknown versions fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_factory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_factory.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_factory.h

Purpose: Common hardware factory interface. Important type is `struct hw_factory`, with `number_of_pins[GPIO_ID_COUNT]` and a `hw_factory_funcs` vtable for initializing DDC/generic/HPD objects, retrieving their base pins, and attaching generation register tables. Important API is `dal_hw_factory_init`. There is no executable control flow in the header. State is the factory object created inside `gpio_service`; it controls service busyness allocation and pin opening. Dependencies are GPIO ids and DC context/gpio forward declarations supplied by includers. Integration is between generation factories and `gpio_service_open`. Risks include optional NULL generic callbacks in older DCE factories, pin count/table count mismatches, and no explicit bounds contract for `en`. Tests should cover vtable completeness per generation, NULL callback handling, and busyness allocation matching factory counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_factory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_generic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_generic.c

Purpose: Hardware generic GPIO mux pin specialization. Important APIs are `dal_hw_generic_init`, `dal_hw_generic_get_pin`, local `set_config`, destructor/destroy helpers, and the static pin vtable. Control flow allocates and constructs a `struct hw_generic`; `set_config` writes `GENERIC_EN` and `GENERIC_SEL` into the generation-attached mux register. State is the `hw_generic` object: embedded `hw_gpio` plus generic register, shift, and mask pointers. Dependencies are `reg_helper.h`, `generic_regs.h`, `hw_gpio`, and generation factory tables. Integration is `dal_gpio_service_create_generic_mux`, `dal_mux_setup_config`, and `gpio_service_open` for `GPIO_ID_GENERIC`. Risks include a likely bounds typo checking `en > GPIO_DDC_LINE_MAX` instead of a generic max, null or zeroed register tables on unsupported generations, unchecked `config_data->type`, and mux writes to zero registers if factory tables are dummy. Tests should cover valid mux enable/select writes, invalid `en`, null config, generations with NULL generic callbacks, and DCN4.2 zero-table behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_generic.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_generic.h

Purpose: Hardware generic mux object declaration. Important type is `struct hw_generic`, embedding `struct hw_gpio` and storing pointers to `generic_registers`, shifts, and masks. Important APIs are `dal_hw_generic_init` and `dal_hw_generic_get_pin`; important macro is `HW_GENERIC_FROM_BASE`. There is no executable control flow in the header. State is populated by generation factories before config writes. Dependencies are `generic_regs.h` and `hw_gpio.h`. Integration is generic mux creation and configuration through the GPIO service. Risks include include guard naming inconsistency, container-cast misuse, null/zero register pointers on unsupported generations, and factory count mismatches. Tests are compile coverage and mux setup paths for DCN generations with real and dummy generic tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_generic.h -->
