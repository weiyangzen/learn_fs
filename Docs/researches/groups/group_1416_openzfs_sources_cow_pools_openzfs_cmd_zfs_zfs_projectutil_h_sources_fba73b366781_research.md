# Group Research: group_1416_openzfs_sources_cow_pools_openzfs_cmd_zfs_zfs_projectutil_h_sources_fba73b366781

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/cow-pools/openzfs`, which is included in subset A. Each listed source file was read completely; symlinked `zpool.d` files were read through their requested paths and interpreted by their invoked basename behavior.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/zfs_projectutil.h -->
# File Research: sources/cow-pools/openzfs/cmd/zfs/zfs_projectutil.h

Small header for `zfs project` command support.

Defines:
- `zfs_project_ops_t`: operation enum for project handling: default, list, check, clear, and set.
- `zfs_project_control_t`: control structure carrying expected project id plus boolean behavior flags for directory-only traversal, ignoring missing entries, preserving project ids, newline formatting, recursive operation, and setting the project flag.
- `zfs_project_handle(const char *name, zfs_project_control_t *zpc)`: exported entry point for applying the selected project operation to a named path or dataset object.

Role:
- Provides the public command-local interface between `zfs_main.c` style command parsing and project quota/id implementation code.
- The structure is policy/configuration only; no implementation or filesystem mutation is in this header.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/zfs_projectutil.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/zfs_util.h -->
# File Research: sources/cow-pools/openzfs/cmd/zfs/zfs_util.h

Shared utility header for the `zfs` command.

Defines:
- Includes `<libzfs.h>` for the userland ZFS handle API.
- C++ linkage guards for mixed C/C++ consumers.
- `safe_malloc(size_t size)`: allocation wrapper expected to terminate or report consistently on failure.
- `nomem(void)`: out-of-memory reporting helper.
- `extern libzfs_handle_t *g_zfs`: process-global libzfs handle used by `zfs` command modules.

Role:
- Centralizes common allocation/error helpers and the global libzfs command handle.
- Contains declarations only; command behavior lives in corresponding `.c` files.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/zfs_util.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/Makefile.am -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/Makefile.am

Automake build/install definition for the `zpool` command and its helper data.

Program build:
- Adds `zpool` to `sbin_PROGRAMS` and `CPPCHECKTARGETS`.
- Sets CFLAGS/CPPFLAGS with common flags plus `libblkid`, `libuuid`, and local include path.
- Builds common sources: `zpool_iter.c`, `zpool_main.c`, `zpool_util.c`, `zpool_util.h`, and `zpool_vdev.c`.
- Adds OS-specific vdev code conditionally: `os/freebsd/zpool_vdev_os.c` for FreeBSD, `os/linux/zpool_vdev_os.c` for Linux.
- Links against `libzfs`, `libzfs_core`, `libnvpair`, `libzutil`, gettext, math, blkid/uuid, and `-lgeom` on FreeBSD.

Installed helper scripts:
- Installs `zpool.d` scripts under `$(zfsexecdir)/zpool.d`.
- Adds these scripts to shellcheck coverage.
- Lists custom-column helpers such as `smart`, SMART aliases, `ses` aliases, `lsblk` aliases, `iostat` aliases, `media`, `dm-deps`, and `upath`.
- `zpoolconfdefaults` controls which helper names get default symlinks under `$(sysconfdir)/zfs/zpool.d`.

Compatibility profiles:
- Installs compatibility feature-set files under `$(pkgdatadir)/compatibility.d`.
- Defines canonical-to-alias symlink pairs for profile names such as years, FreeBSD/TrueNAS/Ubuntu names, GRUB profiles, and OpenZFS version aliases.

Install hook:
- Creates the system `zpool.d` config directory and symlinks default helpers if not already present.
- Creates compatibility alias symlinks forcibly in the compatibility directory.

Role:
- Ties together command compilation, OS-specific implementation selection, helper script distribution, default custom-column availability, and compatibility-profile packaging.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/os/freebsd/zpool_vdev_os.c -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/os/freebsd/zpool_vdev_os.c

FreeBSD-specific `zpool` vdev helper implementation.

Core behavior:
- `check_device()` normalizes device names to `/dev/...` when needed, then delegates validation to `check_file()`.
- `check_file()` delegates to shared `check_file_generic()`.
- `check_sector_size_database()` is a stub returning false; FreeBSD does not use the Linux SCSI inquiry override table here.
- `after_zpool_upgrade()` warns when a pool has `bootfs` set, telling the user they may need to update boot code and referencing `gptzfsboot(8)` and `loader.efi(8)`.
- `zpool_power_current_state()` returns `-1`, marking enclosure slot power state unsupported.
- `zpool_power()` returns `ENOTSUP`, marking slot power control unsupported.

Dependencies:
- Uses FreeBSD device/path headers, `libgeom`, ZFS nvlist/libzutil interfaces, and shared `zpool_util.h`.

Role:
- Supplies the OS abstraction functions required by common `zpool` vdev code.
- FreeBSD validation is intentionally thinner than Linux here and relies on generic file checks plus `/dev` path normalization.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/os/freebsd/zpool_vdev_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/os/linux/zpool_vdev_os.c -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/os/linux/zpool_vdev_os.c

Linux-specific `zpool` vdev validation and enclosure power-control implementation.

Sector-size database:
- Defines `vdev_disk_db_entry_t` and a static table of device inquiry strings known to misreport or require overridden physical sector sizes.
- `check_sector_size_database()` sends a SCSI INQUIRY through `SG_IO`, compares bytes 8-31 against 24-byte database IDs, and returns an override sector size when matched.

Device safety checks:
- `check_slice()` asks `libblkid` for filesystem `TYPE`.
- Empty/unknown type is considered safe.
- `zfs_member` devices are passed to `check_file()` so spare-sharing rules can be applied.
- Non-ZFS filesystems are rejected unless `force` is set.
- `check_disk()` handles whole-disk validation with `O_EXCL` for non-spares, reads EFI/GPT labels with `efi_alloc_and_read()`, scans assigned partitions, and checks each partition path.
- For corrupt primary EFI labels, force allows proceeding via backup-label behavior; otherwise it reports an error.
- `check_device()` owns the `blkid_cache` lifecycle and delegates to `check_disk()`.

Other command hooks:
- `after_zpool_upgrade()` is a Linux no-op.
- `check_file()` delegates to shared `check_file_generic()`.

Sysfs utilities:
- `zpool_sysfs_gets()` reads a sysfs file into an allocated string and strips one trailing newline.
- `zpool_sysfs_puts()` writes a string to a sysfs file.
- `rescan_vdev_config_dev_sysfs_path()` refreshes enclosure sysfs path metadata in a vdev nvlist.

Slot power control:
- `zpool_power_sysfs_path()` finds a vdev with `zpool_find_vdev()`, refreshes enclosure sysfs metadata, then locates either HDD/JBOD `power_status` or NVMe PCI-slot `power`.
- `zpool_power_parse_value()` maps `off`/`0` to 0 and `on`/`1` to 1.
- `zpool_power_use_word()` selects word values for `power_status` and numeric values for `power`.
- `zpool_power_current_state()` reads and parses current power state.
- `zpool_power()` changes state if needed, writes the sysfs value, then polls up to `ZPOOL_POWER_ON_SLOT_TIMEOUT_MS` or 30 seconds by default until the state changes.

Role:
- Implements Linux-specific userland preflight safety for pool device creation.
- Adds Linux-only enclosure/NVMe slot power operations through sysfs.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/os/linux/zpool_vdev_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/ata_err -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/ata_err

Symlink to `smart`; behavior is selected by invoked basename `ata_err`.

Behavior:
- Uses `VDEV_UPATH` when it is a block device, otherwise falls back to `VDEV_PATH`.
- Runs `sudo smartctl -a` when available, or optional developer sample output.
- Parses SMART output with awk.
- For `ata_err`, extracts ATA/SATA `ATA Error Count:` into `ata_err=<count>`.
- If unavailable, prints `ata_err=`.

Role:
- Provides a `zpool status -c ata_err` custom column for ATA error count.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/ata_err -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/cmd_to -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/cmd_to

Symlink to `smart`; behavior is selected by invoked basename `cmd_to`.

Behavior:
- Resolves the vdev path from `VDEV_UPATH` or `VDEV_PATH`.
- Runs and parses `smartctl -a`.
- Extracts SATA `Command_Timeout` raw value into `cmd_to=<value>`.
- Emits `cmd_to=` when no value is found.

Role:
- Provides a custom column for ATA/SATA command timeout count.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/cmd_to -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/defect -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/defect

Symlink to `smart`; behavior is selected by invoked basename `defect`.

Behavior:
- Parses SMART/SAS output from `smartctl -a`.
- Extracts `Elements in grown defect list` into `defect=<value>`.
- Returns an empty `defect=` field if not available.

Role:
- Provides a SAS-focused custom column for grown defect list size.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/defect -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/dm-deps -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/dm-deps

Shell helper for device-mapper dependency reporting.

Behavior:
- `-h` prints help.
- Reads `VDEV_PATH`.
- If the vdev path is a symlink, resolves it with `readlink`.
- Uses the basename as a block device name.
- If `/sys/class/block/<dev>/slaves` exists, lists slave devices in one space-normalized line.
- Always prints `dm-deps=<value>`.

Role:
- Maps a dm/multipath vdev back to underlying block devices for `zpool status -c dm-deps`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/dm-deps -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/enc -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/enc

Symlink to `ses`; behavior is selected by invoked basename `enc`.

Behavior:
- Reads `VDEV_ENC_SYSFS_PATH`.
- If no enclosure sysfs path is set, prints `enc=`.
- For PCI slot paths under `/sys/bus/pci/slots`, returns that sysfs path.
- For normal enclosure paths, lists the parent enclosure directory name.
- Prints `enc=<value>`.

Role:
- Provides the enclosure identifier custom column.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/enc -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/encdev -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/encdev

Symlink to `ses`; behavior is selected by invoked basename `encdev`.

Behavior:
- Reads `VDEV_ENC_SYSFS_PATH`.
- Lists `../device/scsi_generic` below the enclosure slot path.
- Prints `encdev=<sg device>` or `encdev=`.

Role:
- Reports the SCSI generic enclosure device associated with a vdev slot.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/encdev -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/fault_led -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/fault_led

Symlink to `ses`; behavior is selected by invoked basename `fault_led`.

Behavior:
- Reads `VDEV_ENC_SYSFS_PATH`.
- Checks slot `fault` first, then NVMe-style `attention`.
- Prints `fault_led=<value>` or an empty value if unsupported/unavailable.

Role:
- Exposes disk slot fault LED state as a custom column.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/fault_led -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/health -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/health

Symlink to `smart`; behavior is selected by invoked basename `health`.

Behavior:
- Runs/parses `smartctl -a`.
- Supports SAS `SMART Health Status`, SATA `SMART overall-health self-assessment test result`, and NVMe health output.
- Normalizes multi-word SAS health strings with underscores.
- Prints `health=<status>` or `health=`.

Role:
- Provides a drive-reported SMART health custom column across SAS/SATA/NVMe.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/health -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/hours_on -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/hours_on

Symlink to `smart`; behavior is selected by invoked basename `hours_on`.

Behavior:
- Parses SMART power-on time for SAS, SATA, and NVMe.
- SAS: `number of hours powered up`.
- SATA: `Power_On_Hours`.
- NVMe: `Power On Hours`, with punctuation stripped.
- Prints `hours_on=<hours>` or `hours_on=`.

Role:
- Reports drive lifetime powered-on hours.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/hours_on -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/iostat -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/iostat

Shell helper for per-vdev iostat columns.

Behavior:
- `-h` prints helper-specific help.
- Uses `VDEV_UPATH` when it is a block device, otherwise `VDEV_PATH`.
- Exits without output for file-based vdevs.
- On FreeBSD, runs `iostat -dKx`.
- On other systems, runs `iostat -kx`.
- For basename `iostat`, reports since-boot summary stats.
- Parses the final header/data pair and prints every metric except the device-name column as `column=value`.

Role:
- Provides broad iostat bandwidth/latency/utilization metrics as custom zpool columns.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/iostat -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/iostat-10s -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/iostat-10s

Symlink to `iostat`; behavior is selected by invoked basename `iostat-10s`.

Behavior:
- Uses the same vdev path resolution and output parsing as `iostat`.
- Sets interval to 10 seconds and suppresses summary stats where supported.
- Collects one 10-second sample and prints parsed metrics as `column=value`.
- Produces no output for file-based vdevs.

Role:
- Provides sampled 10-second per-vdev iostat custom columns.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/iostat-10s -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/iostat-1s -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/iostat-1s

Symlink to `iostat`; behavior is selected by invoked basename `iostat-1s`.

Behavior:
- Uses the same vdev path resolution and output parsing as `iostat`.
- Sets interval to 1 second and suppresses summary stats where supported.
- Collects one 1-second sample and prints parsed metrics as `column=value`.
- Produces no output for file-based vdevs.

Role:
- Provides sampled 1-second per-vdev iostat custom columns.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/iostat-1s -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/label -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/label

Symlink to `lsblk`; behavior is selected by invoked basename `label`.

Behavior:
- Resolves block path from `VDEV_UPATH` or `VDEV_PATH`.
- Runs `lsblk -dl -n -o label <path>`.
- Trims leading/trailing whitespace.
- Prints `label=<filesystem label>`.

Role:
- Provides a filesystem label custom column for vdev block devices.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/label -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/locate_led -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/locate_led

Symlink to `ses`; behavior is selected by invoked basename `locate_led`.

Behavior:
- Reads `VDEV_ENC_SYSFS_PATH`.
- Reads the slot `locate` sysfs file.
- Prints `locate_led=<value>` or an empty value when unavailable.

Role:
- Exposes enclosure locate LED state for a vdev.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/locate_led -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/lsblk -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/lsblk

Shell helper for common `lsblk`-derived vdev properties.

Behavior:
- `-h` prints basename-specific help.
- If invoked as `lsblk`, reports `size`, `vendor`, and `model`.
- If invoked via another lowercase symlink, uses the basename as an `lsblk --output` column.
- Uses `VDEV_UPATH` when it is a block device, otherwise `VDEV_PATH`.
- Special-cases file vdev size using `du -h --apparent-size`.
- Runs `lsblk -dl -n -o <column> <path>`, trims whitespace, and prints `<column>=<value>`.

Role:
- Provides simple block-device metadata columns for `zpool status -c`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/lsblk -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/media -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/media

Shell helper for classifying vdev media type.

Behavior:
- `-h` prints help.
- If `VDEV_UPATH` is a block device, extracts its basename and reads `/sys/block/<device>/queue/rotational`.
- Maps rotational `0` to `ssd`, `1` to `hdd`, anything else to `invalid`.
- Checks `/sys/block/<device>/device/vpd_pg83` for `iqn.` and overrides media to `iscsi` if found.
- If `VDEV_UPATH` is a regular file, reports `file`.
- Prints `media=<file|hdd|ssd|iscsi|invalid>`.

Role:
- Provides a coarse vdev media-class custom column.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/media -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/model -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/model

Symlink to `lsblk`; behavior is selected by invoked basename `model`.

Behavior:
- Runs `lsblk -dl -n -o model` on the resolved vdev path.
- Trims whitespace.
- Prints `model=<device model>`.

Role:
- Provides disk model number as a custom column.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/model -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/nonmed -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/nonmed

Symlink to `smart`; behavior is selected by invoked basename `nonmed`.

Behavior:
- Parses SAS SMART output.
- Extracts `Non-medium error count` into `nonmed=<count>`.
- Emits `nonmed=` when missing.

Role:
- Reports SAS non-medium error count.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/nonmed -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/nvme_err -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/nvme_err

Symlink to `smart`; behavior is selected by invoked basename `nvme_err`.

Behavior:
- Detects NVMe SMART/health output.
- Extracts `Media and Data Integrity Errors` into `nvme_err=<count>`.
- Emits `nvme_err=` when unavailable.

Role:
- Reports NVMe media/data integrity error count.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/nvme_err -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/off_ucor -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/off_ucor

Symlink to `smart`; behavior is selected by invoked basename `off_ucor`.

Behavior:
- Parses ATA/SATA SMART attributes.
- Extracts `Offline_Uncorrectable` raw value into `off_ucor=<value>`.
- Emits `off_ucor=` when unavailable.

Role:
- Reports offline uncorrectable sector/error count for ATA/SATA devices.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/off_ucor -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/pend_sec -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/pend_sec

Symlink to `smart`; behavior is selected by invoked basename `pend_sec`.

Behavior:
- Parses ATA/SATA SMART attributes.
- Extracts `Current_Pending_Sector` raw value into `pend_sec=<value>`.
- Emits `pend_sec=` when unavailable.

Role:
- Reports pending sector count for ATA/SATA devices.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/pend_sec -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/pwr_cyc -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/pwr_cyc

Symlink to `smart`; behavior is selected by invoked basename `pwr_cyc`.

Behavior:
- Parses SATA `Power_Cycle_Count` or NVMe `Power Cycles`.
- Prints `pwr_cyc=<count>` or `pwr_cyc=`.

Role:
- Reports drive power cycle count.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/pwr_cyc -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/r_proc -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/r_proc

Symlink to `smart`; behavior is selected by invoked basename `r_proc`.

Behavior:
- Parses SAS `read:` SMART statistics.
- Extracts lifetime read gigabytes processed into `r_proc=<value>`.
- Emits `r_proc=` when unavailable.

Role:
- Reports SAS read data processed over drive lifetime.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/r_proc -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/r_ucor -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/r_ucor

Symlink to `smart`; behavior is selected by invoked basename `r_ucor`.

Behavior:
- Parses SAS `read:` SMART statistics.
- Extracts read uncorrectable errors into `r_ucor=<count>`.
- Emits `r_ucor=` when unavailable.

Role:
- Reports SAS read uncorrectable error count.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/r_ucor -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/realloc -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/realloc

Symlink to `smart`; behavior is selected by invoked basename `realloc`.

Behavior:
- Parses ATA/SATA `Reallocated_Sector_Ct`.
- Prints `realloc=<raw count>` or `realloc=`.

Role:
- Reports reallocated sector count for ATA/SATA devices.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/realloc -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/rep_ucor -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/rep_ucor

Symlink to `smart`; behavior is selected by invoked basename `rep_ucor`.

Behavior:
- Parses ATA/SATA `Reported_Uncorrect`.
- Prints `rep_ucor=<raw count>` or `rep_ucor=`.

Role:
- Reports ATA/SATA reported uncorrectable error count.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/rep_ucor -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/serial -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/serial

Symlink to `smart`; behavior is selected by invoked basename `serial`.

Behavior:
- Parses serial number lines from SAS/SATA/NVMe SMART output.
- Prints `serial=<serial number>` or `serial=`.

Role:
- Reports disk serial number through SMART data rather than `lsblk`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/serial -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/ses -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/ses

Shell helper for SCSI Enclosure Services and PCI slot metadata.

Behavior:
- `-h` prints basename-specific help.
- If invoked as `ses`, reports `enc`, `encdev`, `slot`, `fault_led`, and `locate_led`.
- Otherwise reports only the invoked basename.
- Uses `VDEV_ENC_SYSFS_PATH`.
- Handles both normal enclosure paths and NVMe PCI slot paths under `/sys/bus/pci/slots`.
- Reads sysfs files for slot number, fault/attention LED, and locate LED.
- Prints each requested item as `name=value`.

Role:
- Provides enclosure identity, slot, device, and LED state custom columns.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/ses -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/size -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/size

Symlink to `lsblk`; behavior is selected by invoked basename `size`.

Behavior:
- For file-based vdevs, uses `du -h --apparent-size`.
- For block vdevs, runs `lsblk -dl -n -o size`.
- Prints `size=<capacity>`.

Role:
- Reports vdev capacity for both block and file vdevs.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/size -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/slot -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/slot

Symlink to `ses`; behavior is selected by invoked basename `slot`.

Behavior:
- For PCI slot paths, uses the basename of `VDEV_ENC_SYSFS_PATH`.
- For enclosure paths, reads `<VDEV_ENC_SYSFS_PATH>/slot`.
- Prints `slot=<slot>` or `slot=`.

Role:
- Reports enclosure or PCI slot number for a vdev.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/slot -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/smart -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/smart

Main SMART custom-column helper.

Behavior:
- `-h` prints help for the invoked basename.
- Uses `VDEV_UPATH` when valid, otherwise `VDEV_PATH`.
- Runs `sudo smartctl -a` if the target is a block device and `smartctl` exists.
- Includes a developer `samples` hook for parsing saved smartctl outputs.
- Awk parser detects SAS, SATA, and NVMe output and extracts health, temperature, hours, serial, error counters, lifetime processed data, and self-test fields.
- If drive type cannot be detected or smartctl fails, defaults to `sata` with empty values.

When invoked as `smart`:
- SAS columns: `temp`, `health`, `r_ucor`, `w_ucor`.
- SATA columns: `temp`, `health`, `ata_err`, `realloc`, `rep_ucor`, `cmd_to`, `pend_sec`, `off_ucor`.
- NVMe columns: `temp`, `health`, `nvme_err`.

Output:
- Prints found `key=value` lines.
- Prints missing requested keys with empty values so column output remains stable.

Role:
- Aggregates the most important SMART failure-predictor fields for `zpool status -c smart`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/smart -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/smart_test -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/smart_test

Symlink to `smart`; behavior is selected by invoked basename `smart_test`.

Behavior:
- Parses SMART self-test log/status information.
- Reports four fields: `test_type`, `test_status`, `test_progress`, and `test_ended`.
- Converts SATA percent remaining into percent done.
- Computes rough elapsed time since test end when power-on hours are available.
- Emits empty fields for unavailable values.

Role:
- Provides a compact SMART self-test summary custom column group.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/smart_test -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/smartx -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/smartx

Symlink to `smart`; behavior is selected by invoked basename `smartx`.

Behavior:
- Provides extended SMART fields based on drive type.
- SAS: `hours_on`, `defect`, `nonmed`, `r_proc`, `w_proc`.
- SATA: `hours_on`, `pwr_cyc`.
- NVMe: `hours_on`, `pwr_cyc`.
- Prints empty values for missing fields.

Role:
- Complements `smart` with secondary lifetime and diagnostic metrics.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/smartx -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/temp -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/temp

Symlink to `smart`; behavior is selected by invoked basename `temp`.

Behavior:
- Parses temperature from SAS `Drive Temperature`, SATA temperature attributes/current temperature, or NVMe `Temperature`.
- Prints `temp=<celsius>` or `temp=`.

Role:
- Reports drive temperature as a standalone custom column.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/temp -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_ended -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_ended

Symlink to `smart`; behavior is selected by invoked basename `test_ended`.

Behavior:
- Parses latest SMART self-test entry.
- Uses current power-on hours and test lifetime hour to estimate how long ago the test ended.
- Formats days/hours as a compact string such as `1d2h`.
- Prints `test_ended=<age>` or `test_ended=`.

Role:
- Reports approximate completion age of the most recent SMART self-test.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_ended -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_progress -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_progress

Symlink to `smart`; behavior is selected by invoked basename `test_progress`.

Behavior:
- Parses self-test progress from SAS execution status or SATA self-test log.
- Converts SATA percent remaining to percent done.
- Prints `test_progress=<percent/status>` or `test_progress=`.

Role:
- Reports progress of the current or latest SMART self-test.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_progress -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_status -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_status

Symlink to `smart`; behavior is selected by invoked basename `test_status`.

Behavior:
- Parses latest SMART self-test status.
- Normalizes lowercase strings and selected multi-word failure statuses with underscores.
- Maps a parsed `self` status to `running`.
- Prints `test_status=<status>` or `test_status=`.

Role:
- Reports status of the latest SMART self-test.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_status -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_type -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_type

Symlink to `smart`; behavior is selected by invoked basename `test_type`.

Behavior:
- Parses latest SMART self-test type from `# 1` log entries.
- Lowercases and joins the type fields with an underscore.
- Prints `test_type=<type>` or `test_type=`.

Role:
- Reports the latest SMART self-test type, such as short or extended/long variants.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/test_type -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/upath -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/upath

Minimal shell helper for reporting the resolved underlying vdev path.

Behavior:
- `-h` prints help.
- Prints `upath="$VDEV_UPATH"` exactly as supplied by the zpool custom-column environment.

Role:
- Exposes the underlying path selected by ZFS for a vdev.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/upath -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/w_proc -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/w_proc

Symlink to `smart`; behavior is selected by invoked basename `w_proc`.

Behavior:
- Parses SAS `write:` SMART statistics.
- Extracts lifetime write gigabytes processed into `w_proc=<value>`.
- Emits `w_proc=` when unavailable.

Role:
- Reports SAS write data processed over drive lifetime.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/w_proc -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/w_ucor -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/w_ucor

Symlink to `smart`; behavior is selected by invoked basename `w_ucor`.

Behavior:
- Parses SAS `write:` SMART statistics.
- Extracts write uncorrectable errors into `w_ucor=<count>`.
- Emits `w_ucor=` when unavailable.

Role:
- Reports SAS write uncorrectable error count.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool.d/w_ucor -->