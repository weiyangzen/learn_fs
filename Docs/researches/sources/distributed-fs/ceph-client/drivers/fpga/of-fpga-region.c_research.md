# sources/distributed-fs/ceph-client/drivers/fpga/of-fpga-region.c

Purpose: Device Tree support for FPGA regions and overlay-driven FPGA programming. It registers `fpga-region` platform devices, resolves FPGA managers and bridges from DT properties or parent regions, parses overlay image properties, triggers FPGA programming before overlay apply, and releases image/bridge resources after overlay removal.

Important APIs and functions: `of_fpga_region_get_mgr` walks a region and ancestors to find an `fpga-mgr` phandle. `of_fpga_region_get_bridges` adds the parent bridge and `fpga-bridges` phandles from the overlay or region. `of_fpga_region_parse_ov` creates `fpga_image_info` from overlay properties such as `firmware-name`, `partial-fpga-config`, `external-fpga-config`, `encrypted-fpga-config`, and timeout properties. `of_fpga_region_notify` handles overlay pre-apply and post-remove actions. Probe registers an FPGA region and populates child regions.

Control flow: init registers an OF overlay notifier and platform driver. Probe binds DT `fpga-region` nodes to generic region devices. On overlay pre-apply, the notifier finds the target region, rejects child regions that themselves contain `firmware-name`, parses image info, stores it in `region->info`, and calls `fpga_region_program_fpga`. If programming fails, the overlay is rejected and image info is freed. On overlay post-remove, bridges are disabled and put, image info is freed, and `region->info` is cleared.

State and persistence: state includes the notifier, platform driver, each region's manager reference, transient overlay image info, and bridge list references held for the overlay lifetime. Persistent hardware state is the configured FPGA image. DT overlay state controls lifetime of bridge references and image info.

Dependencies and integration points: depends on OF overlay notifications, OF platform population, FPGA manager/bridge/region frameworks, phandle parsing, and platform driver core. It is the main integration between firmware images named in DT overlays and runtime FPGA programming.

Risks and test signals: risks include overlay lifecycle ordering, rejecting nested firmware-name only by matching child regions, ambiguous firmware plus external-config flags, bridge-list cleanup only on post-remove, and manager lookup deferring probe broadly as `-EPROBE_DEFER`. Test signals are `fpga-region` probe logs, overlay pre-apply programming, bridge phandle acquisition, rejected invalid overlays, post-remove bridge put/image free, and timeout flags reaching low-level managers.
