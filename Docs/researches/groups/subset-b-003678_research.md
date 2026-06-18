# Research group subset-b-003678

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf108.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf108.c

### Purpose

`ctxgf108.c` supplies the GF108/Fermi PGRAPH context description used by Nouveau's `gf100` graphics engine. It is mostly a hardware register recipe: static `gf100_gr_init` arrays describe initial context values for internal commands, class methods, hub/GPC/TPC units, and the exported `gf108_grctx` callback table tells the common context generator how to assemble a per-channel graphics context.

### Important APIs, Types, And Functions

The central exported object is `const struct gf100_grctx_func gf108_grctx`. Important public tables include `gf108_grctx_init_9097_0`, `gf108_grctx_init_gpm_0`, `gf108_grctx_init_pe_0`, `gf108_grctx_init_wwdx_0`, and `gf108_grctx_init_tpccs_0`, which are reused by later GF11x files. `gf108_grctx_generate_attrib()` patches per-TPC attribute and alpha offsets into the generated context, while `gf108_grctx_generate_unkn()` applies several live MMIO masks before the context is finalized.

### Control Flow And State

The common `gf100_grctx_generate_main()` path consumes the `hub`, `gpc_0`, `gpc_1`, `tpc`, `icmd`, and `mthd` packs from `gf108_grctx`, writes method/init data, allocates bundle and pagepool state, and calls callback hooks for attribute buffers, SM IDs, TPC counts, ROP mapping, alpha/beta tables, and other topology-dependent registers. `gf108_grctx_generate_attrib()` walks `gr->gpc_nr` and `gr->tpc_nr[gpc]`, calculates beta and alpha regions from `attrib_nr_max * tpc_total`, and patches each TPC's attribute base at `TPC_UNIT(gpc, tpc, 0x500) + 0x20` and alpha base at `+0x44`.

### Dependencies And Integration

The file depends on `ctxgf100.h` for `struct gf100_gr_init`, `struct gf100_gr_pack`, `struct gf100_grctx_func`, context patch helpers, and `TPC_UNIT`; it includes `subdev/fb.h` indirectly for graphics memory context support. It integrates with GF100-generation GR construction through chip-specific GR function tables that select `gf108_grctx` for GF108-class devices. Many register packs reference common GF100/GF104 tables, so changes must stay ABI-compatible with helpers defined in sibling context files.

### Risks And Test Signals

The risks are wrong register defaults, wrong per-TPC offset math, and stale assumptions about `attrib_nr`, `alpha_nr`, `bundle_size`, or pagepool size. Bad values can cause channel context load failures, GPU hangs, or rendering corruption only on GF108-like topologies. Useful test signals are Nouveau module load on GF108 hardware, channel creation/destruction under OpenGL workloads, context switching between multiple clients, suspend/resume, and targeted checks for context-load errors in kernel logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf108.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf110.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf110.c

### Purpose

`ctxgf110.c` adapts the GF100/GF108 context model for GF110-class Fermi GPUs. It provides a GF110 internal-command pack, class method overrides, a small GPC setup override, and the exported `gf110_grctx` function table.

### Important APIs, Types, And Functions

The exported API is `const struct gf100_grctx_func gf110_grctx`, plus reusable method init tables `gf110_grctx_init_9197_0` and `gf110_grctx_init_9297_0`. The file defines `gf110_grctx_pack_icmd`, `gf110_grctx_pack_mthd`, and `gf110_grctx_pack_gpc_0`; it inherits most hub/GPC/TPC behavior from `gf100` and method class `0x9097` from `gf108_grctx_init_9097_0`.

### Control Flow And State

Runtime generation is delegated to `gf100_grctx_generate_main()`. That generator consumes the GF110 packs, then runs inherited callbacks for bundle, pagepool, attributes, SM ID, TPC count, ROP mapping, alpha/beta tables, cache eviction settings, and register `0x419cb8`. There is no custom executable generator in this file; persistence is entirely in static register lists and the constants embedded in `gf110_grctx`.

### Dependencies And Integration

The file depends on `ctxgf100.h` and sibling exports from GF100/GF108. It is part of the Nouveau `nvkm/engine/gr` family selected by GF110 device initialization. It must remain synchronized with method class IDs `0x9097`, `0x9197`, `0x9297`, `0x902d`, `0x9039`, and `0x90c0` because those class packs define the initial channel-visible method state.

### Risks And Test Signals

Risks center on small per-chip deltas: the `0x9297` class block, `0x418830`, and `0x4188fc` setup values differ from related chips and can quietly break context restore. Test signals are GF110 channel bring-up, multi-context 3D workloads, method class initialization coverage, and absence of PGRAPH context faults during repeated context switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf117.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf117.c

### Purpose

`ctxgf117.c` defines the GF117 context layout, bridging late Fermi register packs with Kepler-style PPC-aware topology handling. It introduces PPC pack handling, ROP/tile mapping tailored to GF117, and per-PPC attribute allocation.

### Important APIs, Types, And Functions

The primary export is `const struct gf100_grctx_func gf117_grctx`. Reused exports include `gf117_grctx_pack_gpc_1`, `gf117_grctx_init_pe_0`, and `gf117_grctx_init_wwdx_0`. Important functions are `gf117_grctx_generate_dist_skip_table()`, `gf117_grctx_generate_rop_mapping()`, and `gf117_grctx_generate_attrib()`.

### Control Flow And State

The common main generator applies GF117 hub, GPC, TPC, PPC, internal command, and method packs. `gf117_grctx_generate_attrib()` iterates GPCs and PPCs, skips disabled PPCs through `gr->ppc_mask`, scales alpha/beta allocation by `gr->ppc_tpc_nr[gpc][ppc]`, and patches PPC-local registers. `gf117_grctx_generate_rop_mapping()` packs `gr->tile[]`, `gr->tpc_total`, and `gr->screen_tile_row_offset` into broadcast, TP broadcast, and `UNK78xx` mapping registers. `gf117_grctx_generate_dist_skip_table()` clears eight distribution skip registers.

### Dependencies And Integration

The file depends on `ctxgf100.h`, `subdev/fb.h`, `subdev/mc.h`, and sibling GF108/GF119/GF104 tables. It integrates with chip functions that expose PPC topology through `gr->func->ppc_nr`, `ppc_mask`, `ppc_tpc_nr`, and `ppc_tpc_mask`. Later Kepler and Maxwell files reuse its ROP mapping and PPC attribute model.

### Risks And Test Signals

Topology-derived state is the main risk. Incorrect PPC masks, tile packing, or alpha/beta offsets can corrupt attribute buffers or produce invalid ROP routing on partially fused chips. Test signals include GF117 hardware with asymmetric TPC/PPC configurations, repeated channel context switches, rendering tests that stress ROP/tile paths, and kernel logs for GR context or MMIO faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf117.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf119.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf119.c

### Purpose

`ctxgf119.c` supplies the GF119 late-Fermi context register packs. It extends GF108/GF110 initialization with expanded internal-command coverage, a GF119-specific `0x90c0` method pack, updated front-end, hub, GPC, TPC, texture, MPC, and SM defaults, and the `gf119_grctx` function table.

### Important APIs, Types, And Functions

The exported object is `const struct gf100_grctx_func gf119_grctx`. Exported packs and tables include `gf119_grctx_pack_icmd`, `gf119_grctx_pack_mthd`, `gf119_grctx_init_fe_0`, `gf119_grctx_init_be_0`, `gf119_grctx_init_prop_0`, `gf119_grctx_init_gpc_unk_1`, `gf119_grctx_init_crstr_0`, and `gf119_grctx_init_sm_0`, many of which are reused by GF117 and Kepler files.

### Control Flow And State

There is no custom generator logic. `gf100_grctx_generate_main()` consumes the static packs, then invokes inherited GF108/GF100 callbacks for unknown MMIO setup, bundle/pagepool allocation, attributes, SM IDs, TPC counts, ROP mapping, alpha/beta tables, eviction settings, and `0x419cb8`. The state is persistent only as static register-init data and callback constants.

### Dependencies And Integration

The file depends on `ctxgf100.h` and sibling Fermi table exports. It integrates into Nouveau by providing the GR context function for GF119-family devices and by exporting common pack fragments for later chips. Method pack class IDs cover `0x9097`, `0x9197`, `0x9297`, `0x902d`, `0x9039`, and `0x90c0`.

### Risks And Test Signals

The main risk is accidental breakage of exported tables used outside GF119. Small register defaults in FE/BE/GPC/TPC/SM packs can affect only some chipsets or graphics classes. Test signals are GF119 and GF117 boot/channel tests, class method initialization tests, OpenGL workloads with context switching, and absence of PGRAPH traps after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf119.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk104.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk104.c

### Purpose

`ctxgk104.c` implements Kepler GK104 graphics context generation. It contains large Kepler register packs and adds generator callbacks for bundle/pagepool programming, LTC context patching, unknown live MMIO enables, GPC/TPC count state, ROP/tile mapping reuse, and Kepler alpha/beta distribution tables.

### Important APIs, Types, And Functions

The primary export is `const struct gf100_grctx_func gk104_grctx`. Exported reusable data and helpers include `gk104_grctx_pack_icmd`, `gk104_grctx_init_a097_0`, `gk104_grctx_init_memfmt_0`, `gk104_grctx_init_ds_0`, `gk104_grctx_init_scc_0`, `gk104_grctx_pack_hub`, `gk104_grctx_init_gpm_0`, `gk104_grctx_pack_tpc`, `gk104_grctx_init_pes_0`, and `gk104_grctx_pack_ppc`. Important functions are `gk104_grctx_generate_bundle()`, `gk104_grctx_generate_pagepool()`, `gk104_grctx_generate_patch_ltc()`, `gk104_grctx_generate_unkn()`, `gk104_grctx_generate_gpc_tpc_nr()`, `gk104_grctx_generate_alpha_beta_tables()`, and the local `gk104_grctx_generate_r419f78()`.

### Control Flow And State

`gf100_grctx_generate_main()` drives generation using the GK104 packs and callback table. `gk104_grctx_generate_bundle()` delegates to GF100 bundle setup, then patches `0x4064c8` from the configured GPM FIFO depth and token limit. `gk104_grctx_generate_pagepool()` enables pagepool state at `0x4064cc`. `gk104_grctx_generate_patch_ltc()` reads live LTC registers `0x17e91c` and `0x17e920` and patches those values into the generated context. `gk104_grctx_generate_alpha_beta_tables()` computes per-GPC/PPC masks for 32 balancing slots and writes `0x406800`/`0x406c00` tables.

### Dependencies And Integration

This file depends on `ctxgf100.h`, `subdev/fb.h`, `subdev/mc.h`, and GF117/GF119 reusable packs. It is a base for later GK110, GK208, Maxwell, Pascal, and Volta helpers, so its exported helpers are part of the local context ABI inside `nvkm/engine/gr`. It integrates with runtime topology state such as `gpc_nr`, `tpc_total`, `ppc_tpc_nr`, and `ppc_tpc_mask`.

### Risks And Test Signals

Risks include incorrect alpha/beta masks on fused topologies, wrong bundle token limits, stale live LTC patching, and fragile unknown MMIO masks. The comment around `r418800` explicitly records uncertainty. Test signals include GK104 hardware boot, multi-channel context switching, workloads that stress pixel/attribute paths, lockups around helper invocation loads controlled by `0x419f78`, and comparisons across fully enabled and fused chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk110.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk110.c

### Purpose

`ctxgk110.c` adapts the GK104 Kepler context system for GK110. It provides GK110 internal-command and method packs, hub/GPC/TPC/PPC register defaults, and a few register workarounds for SM behavior.

### Important APIs, Types, And Functions

The main export is `const struct gf100_grctx_func gk110_grctx`. Reusable exports include `gk110_grctx_pack_icmd`, `gk110_grctx_pack_mthd`, `gk110_grctx_init_pri_0`, `gk110_grctx_init_cwd_0`, `gk110_grctx_pack_hub`, `gk110_grctx_init_gpc_unk_2`, `gk110_grctx_pack_gpc_0`, `gk110_grctx_pack_gpc_1`, `gk110_grctx_init_tex_0`, `gk110_grctx_init_mpc_0`, `gk110_grctx_init_l1c_0`, and `gk110_grctx_pack_ppc`. Functions `gk110_grctx_generate_r419eb0()` and `gk110_grctx_generate_r419f78()` patch live SM registers.

### Control Flow And State

Generation uses `gf100_grctx_generate_main()`, GK110 static packs, GK104 bundle/pagepool/LTC/topology helpers, and GF117 PPC attribute handling. The GK110 table changes bundle token limit to `0x7c0`, keeps the `0x3000` bundle size and `0x8000` pagepool, and adds `r419eb0`/`r419f78` hooks. `gk110_grctx_generate_r419eb0()` sets bit `0x1000`; `gk110_grctx_generate_r419f78()` clears bit 3 to keep loads enabled in FP helper invocations.

### Dependencies And Integration

The file depends on `ctxgf100.h` plus GK104 and GF117 helper exports. It is itself a base for GK110B and GK208 variants. It integrates with class `0xa197` method initialization and Nouveau GR engine setup for GK110 devices.

### Risks And Test Signals

Risks are GK110-specific register deltas, especially SM/L1C/MPC values and token limits. Incorrect `0x419f78` handling can affect shader helper invocation semantics. Test signals include GK110 OpenGL/compute rendering, multi-context stress, fused topology tests, and shader workloads that exercise helper loads and SM state restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk110b.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk110b.c

### Purpose

`ctxgk110b.c` is a narrow GK110B revision override. It reuses GK110 context generation almost entirely but replaces the SM init table and TPC pack, then exports `gk110b_grctx`.

### Important APIs, Types, And Functions

The main export is `const struct gf100_grctx_func gk110b_grctx`. The only local static data is `gk110b_grctx_init_sm_0` and `gk110b_grctx_pack_tpc`, which combine GF117 PE, GK110 TEX/MPC/L1C, and GK110B SM defaults.

### Control Flow And State

There is no custom runtime function. `gf100_grctx_generate_main()` consumes GK110 hub, GPC, PPC, ICMD, and method packs plus the GK110B TPC pack. Bundle, pagepool, attributes, LTC patching, topology, ROP mapping, alpha/beta tables, and SM register workarounds come from GK104/GK110/GF117 helpers.

### Dependencies And Integration

The file depends on `ctxgf100.h` and the GK110/GK104/GF117 exported helpers. It integrates as the context function selected by GK110B-class device descriptors.

### Risks And Test Signals

Risk is concentrated in the SM defaults, especially `0x419f70`, `0x419f78`, and related SM context fields that differ from GK110. Test signals are GK110B boot, graphics channel creation, shader-heavy workloads, and comparison with GK110 behavior to catch revision-specific regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk110b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk208.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk208.c

### Purpose

`ctxgk208.c` defines the context register packs and callback table for GK208 Kepler GPUs. It mixes GK110/GK104 infrastructure with GK208-specific ICMD, FE, hub, GPC, TPC, PPC, texture, SM, and CBM defaults.

### Important APIs, Types, And Functions

The exported object is `const struct gf100_grctx_func gk208_grctx`. Reusable exported tables include `gk208_grctx_init_rstr2d_0`, `gk208_grctx_init_prop_0`, `gk208_grctx_init_crstr_0`, and the local pack tables for ICMD, hub, GPC, TPC, and PPC. The function table reuses `gk104_grctx_generate_bundle()`, `gk104_grctx_generate_pagepool()`, `gf117_grctx_generate_attrib()`, `gk104_grctx_generate_patch_ltc()`, `gf117_grctx_generate_rop_mapping()`, and `gk110_grctx_generate_r419f78()`.

### Control Flow And State

The common main generator applies GK208 static packs, then calls inherited topology and buffer callbacks. Important constants are bundle size `0x3000`, minimum GPM FIFO depth `0xc2`, token limit `0x200`, pagepool size `0x8000`, alpha count `0x648`, and `alpha_nr_max` `0x7ff`. The ICMD table is GK208-specific and includes additional `0x00c4xx`/`0x00c5xx` entries not present in earlier Kepler variants.

### Dependencies And Integration

The file depends on `ctxgf100.h` and sibling GK104/GK110/GF117 table exports. It integrates with GK208 device GR setup and shares many helper callbacks with other Kepler chips, while providing lower token/FIFO limits appropriate to this smaller GPU.

### Risks And Test Signals

Risks are mis-sized bundle limits, incorrect GK208-specific ICMD ranges, and mismatched inherited helpers on smaller fused topologies. Test signals include GK208 channel creation, desktop OpenGL workloads, suspend/resume, context switching between clients, and absence of PGRAPH traps involving `0x00c4xx` or SM state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk208.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk20a.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk20a.c

### Purpose

`ctxgk20a.c` implements the Tegra GK20A graphics context main sequence. Unlike desktop Kepler files, it does not provide static hub/GPC/TPC packs; it defines a custom `main` callback for the SoC path and exports a compact `gk20a_grctx` function table.

### Important APIs, Types, And Functions

The main function is `gk20a_grctx_generate_main()`, and the exported object is `const struct gf100_grctx_func gk20a_grctx`. The callback table reuses GK104 bundle/pagepool generation, GF117 attributes, GF100 SM/TPC helpers, GF117 ROP mapping, and GK104 alpha/beta tables.

### Control Flow And State

`gk20a_grctx_generate_main()` writes the software MMIO context, waits for idle, temporarily clears idle timeout register `0x404154`, emits attribute buffer and attribute layout, applies unknown MMIO setup, floorsweeps, clears the eight distribution skip registers, writes `0x405b00` from `tpc_total` and `gpc_nr`, sets bit `0x08000000` in `0x5044b0`, restores idle timeout, loads method and ICMD streams, and finally patches pagepool and bundle buffers. The table sets bundle size `0x1800`, FIFO depth `0x62`, token limit `0x100`, and GK20A-specific attribute sizes.

### Dependencies And Integration

The file depends on `ctxgf100.h`, `gf100.h`, and `subdev/mc.h`. It integrates with Tegra GK20A GR initialization where firmware/device behavior differs enough to need a custom main sequence but still uses GF100-family context patch helpers.

### Risks And Test Signals

Risks include idle-timeout handling, missing static packs that desktop chips rely on, SoC-specific register `0x5044b0`, and attribute sizing. Test signals are GK20A/Tegra boot, channel creation, graphics workloads under runtime PM, and logs around idle waits or context-load failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgm107.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgm107.c

### Purpose

`ctxgm107.c` implements Maxwell GM107 context generation. It provides Maxwell register packs and changes attribute, bundle, pagepool, attribute-buffer, and SM-ID programming from the Kepler model.

### Important APIs, Types, And Functions

The primary export is `const struct gf100_grctx_func gm107_grctx`. Important helpers are `gm107_grctx_generate_bundle()`, `gm107_grctx_generate_pagepool()`, `gm107_grctx_generate_attrib()`, `gm107_grctx_generate_attrib_cb()`, `gm107_grctx_generate_sm_id()`, and local hooks for `r406500` and `r419e00`. Exported reusable tables include `gm107_grctx_init_gpc_unk_0` and `gm107_grctx_init_wwdx_0`.

### Control Flow And State

The common main generator consumes GM107 ICMD, method, hub, GPC, TPC, and PPC packs. `gm107_grctx_generate_bundle()` patches bundle addresses into both SCC and GPC paths (`0x408004/0x408008` and `0x418e24/0x418e28`) and writes token/FIFO limits. `gm107_grctx_generate_attrib()` lays out alpha/attrib regions per PPC, patches PPC base and size registers, and writes per-PPC usage registers at `0x418ea0 + n * 4`. `gm107_grctx_generate_attrib_cb()` calls the GF100 implementation and patches `0x419c2c` with the buffer address. `gm107_grctx_generate_sm_id()` writes SM IDs to three per-TPC/GPC locations.

### Dependencies And Integration

The file depends on `ctxgf100.h`, `subdev/fb.h`, `subdev/mc.h`, and reusable GK104/GK110/GK208/GF117 helpers. It is the base for GM200/GM20B and later Pascal helpers. It integrates with topology fields such as `ppc_tpc_nr`, `ppc_tpc_max`, `tpc_total`, and SM numbering.

### Risks And Test Signals

Risks include attribute buffer sizing and address patching, Maxwell-specific bundle paths, and SM ID writes that differ from Kepler. Test signals include GM107 hardware boot, multi-context OpenGL, fused topology coverage, pagepool/bundle address validation, and shader workloads sensitive to SM ID or attribute state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgm200.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgm200.c

### Purpose

`ctxgm200.c` defines high-level GM200 Maxwell context behavior by reusing GM107 generators and adding GM200-specific topology and register hooks. It contains no static register packs.

### Important APIs, Types, And Functions

The main export is `const struct gf100_grctx_func gm200_grctx`. Important functions are `gm200_grctx_generate_r419a3c()`, `gm200_grctx_generate_smid_config()`, `gm200_grctx_generate_tpc_mask()`, `gm200_grctx_generate_r406500()`, `gm200_grctx_generate_dist_skip_table()`, and the local `gm200_grctx_generate_r418e94()`.

### Control Flow And State

The common main generator uses inherited GM107 bundle/pagepool/attribute callbacks, then invokes GM200 hooks. `gm200_grctx_generate_smid_config()` builds a compact SM distribution table at `0x405b60` and per-GPC SM maps at `0x405ba0`. `gm200_grctx_generate_tpc_mask()` writes enabled TPC masks to `0x4041c4`. `gm200_grctx_generate_dist_skip_table()` computes skip masks by removing the minimum active TPCs per PPC and writes eight `0x4064d0` registers. The table uses pagepool size `0x20000`, bundle token limit `0x780`, and smaller attrib counts than GM107.

### Dependencies And Integration

The file depends on `ctxgf100.h` and GM107/GK104/GF117 helpers. It integrates with device topology fields `sm[]`, `sm_nr`, `gpc_nr`, `tpc_nr`, `ppc_tpc_nr`, `ppc_tpc_mask`, and `ppc_tpc_min`.

### Risks And Test Signals

Risks are topology packing mistakes in SMID and skip tables, incorrect TPC masks on fused chips, and register hooks with full-register masks. Test signals include GM200 cards with non-uniform TPC layouts, channel switches, shader scheduling tests, and kernel logs for context or SM mapping errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgm20b.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgm20b.c

### Purpose

`ctxgm20b.c` implements the Tegra GM20B graphics context main sequence. It mirrors the SoC-specific GK20A flow but uses Maxwell/GM107 buffer and attribute generation plus GM200 SMID configuration.

### Important APIs, Types, And Functions

The main function is `gm20b_grctx_generate_main()`, and the exported object is `const struct gf100_grctx_func gm20b_grctx`. The table uses `gm107_grctx_generate_bundle()`, `gm107_grctx_generate_pagepool()`, `gm107_grctx_generate_attrib_cb()`, `gm107_grctx_generate_attrib()`, `gm107_grctx_generate_sm_id()`, and `gf117_grctx_generate_rop_mapping()`.

### Control Flow And State

`gm20b_grctx_generate_main()` writes SW context MMIO, waits idle, temporarily clears idle timeout `0x404154`, emits attribute buffer and layout, applies unknown MMIO setup, floorsweeps, clears `0x4064d0` skip registers, writes GPC/TPC count to `0x405b00`, derives `0x408908` from `0x410108 | 0x80000000`, builds and writes a packed TPC mask to `0x4041c4`, emits GM200 SMID config, restores idle timeout, and emits method, ICMD, pagepool, and bundle state. The function table uses bundle size `0x1800`, token limit `0x1c0`, and GM20B-specific attribute counts.

### Dependencies And Integration

The file depends on `ctxgf100.h` and GM107/GM200 helpers. It integrates with Tegra GM20B GR initialization where the SoC path needs a custom main sequence and smaller resource limits than desktop Maxwell.

### Risks And Test Signals

Risks include SoC-specific register ordering, idle wait failures, TPC mask packing, and SMID map generation. Test signals are GM20B/Tegra boot, runtime-PM transitions, graphics workloads with multiple channels, and absence of context-load or idle-timeout messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgm20b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp100.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp100.c

### Purpose

`ctxgp100.c` implements Pascal GP100 context-generation differences: new pagepool programming, GP100 attribute layout, attribute-buffer sizing, and an expanded SMID map format. It exports `gp100_grctx`.

### Important APIs, Types, And Functions

Important functions are `gp100_grctx_generate_pagepool()`, the local `gp100_grctx_generate_attrib()`, `gp100_grctx_generate_attrib_cb()`, `gp100_grctx_generate_attrib_cb_size()`, and `gp100_grctx_generate_smid_config()`. The exported callback table is `const struct gf100_grctx_func gp100_grctx`.

### Control Flow And State

`gp100_grctx_generate_pagepool()` patches pagepool base and control into `0x40800c/0x408010` and `0x419004/0x419008`. `gp100_grctx_generate_attrib()` separates attribute and alpha count registers (`0x405830`, `0x40585c`), lays out alpha first then attrib regions, allocates attrib space by `attrib_nr_max * ppc_tpc_max`, and clears `0x418eec` and `0x41befc`. `gp100_grctx_generate_attrib_cb_size()` computes the backing buffer size from alpha plus all PPC-max attrib regions, aligned to 128 bytes. `gp100_grctx_generate_smid_config()` writes distribution and per-GPC/TPC-group SM maps.

### Dependencies And Integration

The file depends on `ctxgf100.h`, `subdev/fb.h`, and GM107/GM200/GK104/GF117 helpers. It is the base for GP102/GP104/GP107 and shares its pagepool and SMID logic with those variants.

### Risks And Test Signals

Risks are buffer-size underestimation, address alignment, PPC-max versus active-TPC accounting, and SMID map indexing. Test signals include GP100 channel creation, multiple fused topology cases, Pascal shader workloads, context-switch stress, and pagepool/attribute buffer fault absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp102.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp102.c

### Purpose

`ctxgp102.c` defines Pascal GP102/large-Pascal context differences over GP100. It introduces GFXP-sized attribute regions, a GP102 attribute-buffer size calculation, and a `0x408840` register hook.

### Important APIs, Types, And Functions

The exported object is `const struct gf100_grctx_func gp102_grctx`. Important functions are `gp102_grctx_generate_attrib()`, `gp102_grctx_generate_attrib_cb_size()`, and the local `gp102_grctx_generate_r408840()`.

### Control Flow And State

`gp102_grctx_generate_attrib()` writes attribute, alpha, and max-batch registers, then walks active PPCs. It patches PPC `+0xc0` with `gfxp_nr * ppc_tpc_max`, writes per-GPC attribute size at `GPC_UNIT(gpc, 0xc44 + ppc * 4)`, manages attrib and alpha offsets, and writes per-PPC usage at `0x418ea0 + n * 4`. It also patches `0x4181e4` and `0x41befc` to `0x100`. The size helper sums alpha state plus `gfxp_nr * ppc_nr * ppc_tpc_max` for each GPC, aligned to 128 bytes.

### Dependencies And Integration

The file depends on `ctxgf100.h`, `subdev/fb.h`, GP100 pagepool/attrib-CB/SMID helpers, GM107 bundle/SMID helpers, GM200 topology hooks, and GK104 unknown setup. GP104 and GP107 reuse these GP102 attribute helpers with different constants.

### Risks And Test Signals

Risks include using `gfxp_nr` incorrectly, underallocating attribute buffers, and applying GP102-only `0x408840` behavior to the wrong chip. Test signals include GP102 rendering and context switching, shader workloads that stress GFXP state, fused topology coverage, and checks for context buffer overruns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp104.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp104.c

### Purpose

`ctxgp104.c` is a compact Pascal GP104 context descriptor. It reuses GP102/GP100/GM107/GM200 helpers and only supplies GP104-specific resource constants in `gp104_grctx`.

### Important APIs, Types, And Functions

The sole export is `const struct gf100_grctx_func gp104_grctx`. It references `gp102_grctx_generate_attrib_cb_size()`, `gp100_grctx_generate_attrib_cb()`, `gp102_grctx_generate_attrib()`, `gp100_grctx_generate_pagepool()`, `gm107_grctx_generate_bundle()`, `gp100_grctx_generate_smid_config()`, and GM200/GK104/GF117 topology hooks.

### Control Flow And State

Runtime control flow is entirely inherited from `gf100_grctx_generate_main()` and the referenced helpers. GP104 uses bundle token limit `0x900`, pagepool size `0x20000`, `attrib_nr_max` `0x4b0`, `attrib_nr` `0x320`, alpha max/count `0xc00`/`0x800`, and `gfxp_nr` `0xba8`. It does not install GP102's `r408840` hook.

### Dependencies And Integration

The file depends on `ctxgf100.h` and helper symbols from GP102, GP100, GM107, GM200, GK104, and GF117. It integrates with GP104 device descriptors as a constants-only context variant.

### Risks And Test Signals

Risks are wrong constants for GP104 relative to GP102 or GP107, especially `gfxp_nr` and token limit. Test signals include GP104 hardware channel initialization, graphics workloads with context switching, and validation that GP102-only `r408840` behavior is not required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp107.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp107.c

### Purpose

`ctxgp107.c` is the Pascal GP107 context descriptor. Like GP104, it reuses GP102/GP100 helper logic and adjusts only resource limits for the smaller chip.

### Important APIs, Types, And Functions

The sole export is `const struct gf100_grctx_func gp107_grctx`. It references GP102 attribute helpers, GP100 pagepool/attrib-CB/SMID helpers, GM107 bundle and SM-ID helpers, and GM200/GK104/GF117 topology helpers.

### Control Flow And State

Generation is inherited. GP107 sets bundle token limit `0x300`, pagepool size `0x20000`, `attrib_nr_max` `0x15de`, `attrib_nr` `0x540`, alpha max/count `0xc00`/`0x800`, and `gfxp_nr` `0xe94`. Those constants feed the GP102 attribute-buffer size and per-PPC layout logic.

### Dependencies And Integration

The file depends on `ctxgf100.h` and the Pascal/Maxwell helper stack. It integrates with GP107 device initialization as a constants-only variant.

### Risks And Test Signals

Risks are attribute-buffer sizing and token limit mismatches on small Pascal GPUs. Test signals include GP107 boot, channel creation, OpenGL workloads, context-switch stress, and absence of attribute/pagepool memory faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgv100.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgv100.c

### Purpose

`ctxgv100.c` implements Volta GV100 context-generation differences. It adds a software VEID bundle-init pack, Volta attribute layout and attribute-buffer programming, non-PES-aware SM ID mapping, wider ROP mapping, and several live MMIO hooks.

### Important APIs, Types, And Functions

The exported object is `const struct gf100_grctx_func gv100_grctx`. Important APIs include `gv100_grctx_generate_attrib()`, `gv100_grctx_generate_attrib_cb()`, `gv100_grctx_generate_rop_mapping()`, `gv100_grctx_generate_r400088()`, `gv100_grctx_generate_unkn()`, `gv100_grctx_unkn88c()`, and the local `gv100_grctx_generate_sm_id()`. The file also defines `gv100_grctx_pack_sw_veid_bundle_init`.

### Control Flow And State

The common main generator uses inherited bundle/pagepool and topology hooks plus GV100-specific callbacks. `gv100_grctx_generate_attrib()` follows GP102-style GFXP allocation but does not write the per-GPC `0xc44` register. `gv100_grctx_generate_attrib_cb()` patches the attribute buffer at `0x419e00/0x419e04`. `gv100_grctx_generate_rop_mapping()` writes tile maps to broadcast, TP broadcast, and `UNK78xx` registers using a map length derived from maximum GPC/TPC capacity and 5-bit tile values. `gv100_grctx_generate_sm_id()` converts TPC IDs with `gv100_gr_nonpes_aware_tpc()` before writing SM IDs. `unkn88c` toggles bit `0x10` in three registers with readbacks.

### Dependencies And Integration

The file depends on `ctxgf100.h` plus GV100 GR topology helpers, GP102 sizing, GP100 pagepool/SMID logic, GM107 bundle/attrib base programming, and GM200 distribution hooks. It integrates with Volta context setup, including VEID bundle initialization absent from earlier chips.

### Risks And Test Signals

Risks include non-PES TPC remapping, larger tile-map packing, VEID bundle-init correctness, and live MMIO toggles that can affect context isolation. Test signals include GV100 channel creation, context switching with multiple VEIDs where supported, shader workloads, fused topology mapping, and checking for GR faults around `0x40988c`, `0x41a88c`, or ROP map registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgv100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxnv40.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxnv40.c

### Purpose

`ctxnv40.c` builds the NV40-era PGRAPH context program and default context values. Unlike GF100+ files that describe register packs through `gf100_grctx_func`, this file emits microcode-like context-program instructions and fills a GPU object with default register state for NV40/NV4x/NV6x class devices.

### Important APIs, Types, And Functions

The exported entry points are `nv40_grctx_init()` and `nv40_grctx_fill()`. Major internal constructors are `nv40_gr_construct_general()`, `nv40_gr_construct_state3d()`, `nv40_gr_construct_state3d_2()`, `nv40_gr_construct_state3d_3()`, `nv40_gr_construct_shader()`, and `nv40_grctx_generate()`. `nv40_gr_vs_count()` selects vertex-shader count from chipset ID. The file defines CP instruction/flag macros consumed by the inline helpers in `ctxnv40.h`.

### Control Flow And State

`nv40_grctx_init()` allocates a 256-instruction buffer, runs `nv40_grctx_generate()` in `NVKM_GRCTX_PROG` mode, writes the generated program to PGRAPH registers `0x400324/0x400328`, returns context value size through `*size`, and frees the buffer. `nv40_grctx_fill()` runs the same generator in `NVKM_GRCTX_VALS` mode to write defaults into a `struct nvkm_gpuobj`. `nv40_grctx_generate()` emits branch/wait/set logic for auto/user save and load, swaps general state, conditional 3D state, a random state block, and per-vertex-shader state, then clears pending flags and ends. Constructors use `cp_ctx()` to reserve context ranges and `gr_def()` to write defaults in fill mode.

### Dependencies And Integration

The file depends on `ctxnv40.h` for generator state and CP helpers, `nv40.h` for `nv44_gr_class()`, core GPU object writes, chipset IDs, and PGRAPH MMIO access. It integrates with NV40 GR initialization, which calls `nv40_grctx_init()` for the hardware context program and `nv40_grctx_fill()` for per-channel context memory.

### Risks And Test Signals

Risks are high because CP instruction encoding, branch label patching, register ranges, context size accounting, and chipset-specific shader lengths all must agree. The comment block documents unimplemented NVIDIA context-program paths, so rare interrupt/save/load cases may differ from proprietary behavior. Test signals include NV40/NV44/NV4x/NV6x hardware boot, context program upload size under 256 instructions, channel creation, 3D rendering, vertex shader workloads across different VS counts, and save/load stress with PGRAPH interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxnv40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxnv40.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxnv40.h

### Purpose

`ctxnv40.h` defines the tiny builder API used by `ctxnv40.c` and `ctxnv50.c` to emit NV40/NV50-style PGRAPH context programs and default context values. It holds `struct nvkm_grctx` and inline helpers for context-program output, labels, branches, waits, flag updates, position changes, and default register writes.

### Important APIs, Types, And Functions

The key type is `struct nvkm_grctx`, which stores the device, generation mode (`NVKM_GRCTX_PROG` or `NVKM_GRCTX_VALS`), output instruction buffer, GPU object target, program limits/labels, current context register, and context value positions. Helpers are `cp_out()`, `cp_lsr()`, `cp_ctx()`, `cp_name()`, `_cp_bra()` with `cp_bra`/`cp_cal`/`cp_ret`, `_cp_wait()` with `cp_wait`, `_cp_set()` with `cp_set`, `cp_pos()`, and `gr_def()`.

### Control Flow And State

In program mode, helpers append instructions to `ctx->ucode`, track `ctxprog_len`, and resolve forward branch placeholders when `cp_name()` later defines a label. `cp_ctx()` converts MMIO register addresses into context register indexes, advances `ctxvals_pos`, emits long-length load-state-register sequences when needed, and emits a CP context instruction. In value mode, most CP helpers are no-ops; `gr_def()` maps an MMIO register to the reserved context value offset and writes the default into `ctx->data`.

### Dependencies And Integration

The header depends on `<core/gpuobj.h>` for `struct nvkm_gpuobj` and `nvkm_wo32()`. It relies on CP opcode and flag macros being defined by the including `.c` file before use, which is why `ctxnv40.c` defines `CP_*` values before including it. It integrates with NV40/NV50 context generators as an internal DSL.

### Risks And Test Signals

Risks include label patching mistakes, unchecked label indexes beyond 32, `BUG_ON()` if a program exceeds `ctxprog_max`, incorrect `ctxvals_pos` accounting, and the implicit dependency on include-order macros. Test signals are successful builds of NV40/NV50 generators, context program generation without `BUG_ON`, correct returned context sizes, and runtime validation on old GPUs that context defaults land at expected offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxnv40.h -->
