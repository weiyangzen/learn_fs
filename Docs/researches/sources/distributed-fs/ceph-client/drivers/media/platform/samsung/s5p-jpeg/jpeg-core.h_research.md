# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-core.h

Purpose: shared private definitions for the Samsung JPEG codec driver.

Important types and constants: declares driver name, clock count, compression quality range, RGB-to-YCbCr coefficients, IRQ timeout, format flags, encode/decode modes, queue type ids, subsampling ids, marker limits, and version enums. `struct s5p_jpeg` is the global device abstraction. `struct s5p_jpeg_variant` stores version, format flag, compatibility quirks, m2m ops, IRQ handler, and clock names. `struct s5p_jpeg_fmt` describes fourcc, depth, plane counts, alignment, subsampling, and direction/variant flags. `struct s5p_jpeg_q_data` stores queue format, dimensions, JPEG marker offsets, and buffer size. `struct s5p_jpeg_ctx` is per-file codec state.

Control flow role: included by the common core and all hardware helpers so they share variant IDs, mode constants, address structure, and context/device layouts.

State and persistence: defines in-memory state only. Header parsing results persist in `s5p_jpeg_q_data` for the lifetime of a context or until the next output format/header update.

Dependencies and integration: includes Linux interrupt, media JPEG marker definitions, V4L2 device/file-handle/control headers. Hardware helper headers consume `struct s5p_jpeg_addr` and mode/version constants.

Risks: format flags control which formats userspace can request for each variant and direction; mistakes expose unsupported hardware combinations. `S5P_JPEG_MAX_MARKER` limits stored DHT/DQT marker segments and can reject complex JPEGs.

Test signals: compile coverage across all helper files, format enumeration per variant, control defaults per encode/decode mode, and header parser tests that validate marker storage limits.
