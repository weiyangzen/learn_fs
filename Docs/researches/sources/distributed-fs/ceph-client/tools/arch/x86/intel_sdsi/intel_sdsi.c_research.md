# sources/distributed-fs/ceph-client/tools/arch/x86/intel_sdsi/intel_sdsi.c

## Purpose
Implements the Intel On Demand/SDSi command-line tool for listing auxiliary SDSi devices, displaying socket registers, reading state and meter certificates, and provisioning AKC or CAP payloads through sysfs.

## APIs, Types, and Functions
Important state structs mirror sysfs binary layouts: `sdsi_regs`, `state_certificate`, `license_key_info`, `license_blob_content`, `meter_certificate`, `bundle_encoding_counter`, and `sdsi_dev`. Main helpers include `sdsi_list_devices()`, `sdsi_update_registers()`, `sdsi_read_reg()`, `sdsi_meter_cert_show()`, `sdsi_state_cert_show()`, `sdsi_provision()`, `sdsi_provision_akc()`, `sdsi_provision_cap()`, `read_sysfs_data()`, `sdsi_create_dev()`, and `main()`.

## Control Flow, State, and Persistence
`main()` parses one command and optional device number. Device creation builds `/sys/bus/auxiliary/devices/intel_vsec.sdsi.N`, opens it, reads `guid`, and stores the path/name. Read paths refresh `registers`, validate GUID-specific register byte counts, check feature availability, then read `state_certificate`, `meter_certificate`, or `meter_current` into fixed 4 KiB buffers for parsing. Provisioning opens a user binary and writes it to `provision_akc` or `provision_cap` after checking update availability and failure thresholds.

## Dependencies and Integration
Uses POSIX file, directory, getopt, realpath, and sysfs APIs. The sysfs contract is provided by the Intel VSEC SDSi kernel driver and exposes device files `guid`, `registers`, certificate blobs, and provisioning endpoints.

## Risks and Test Signals
Risks include trusting certificate-internal sizes before full bounds validation, fixed 4 KiB payload limits, `chdir()` global process state, typo-prone human output, and a suspicious `if (!access(optarg, F_OK) == 0)` expression. Test signals are mocked sysfs directories for each command, malformed certificate size tests, GUID v1/v2 register-size tests, provisioning failure injection, and real hardware smoke tests gated by update limits.
