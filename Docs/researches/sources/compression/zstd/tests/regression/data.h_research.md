# sources/compression/zstd/tests/regression/data.h

Purpose: This header declares the dataset and buffer abstraction for the regression harness. It lets compression methods treat file and directory datasets uniformly while still exposing dictionaries and cache initialization.

Important APIs and types: `data_type_t` distinguishes a single file from a directory. `data_resource_t` stores a download URL, expected XXH64, and derived local path. `data_t` combines data and dictionary resources, type, and logical name. `data_buffer_t` owns a byte pointer, size, and capacity. `data_buffers_t` represents multiple buffers for directory datasets. Public functions cover dictionary availability, cache lifecycle, reading dataset data/dictionaries, direct file reads, buffer allocation, comparison, and freeing.

Control flow: The header has no implementation flow, but its contracts drive the harness: `test.c` calls `data_init()` and `data_finish()`, `method.c` loads `data_buffers_t` and optional dictionaries per dataset, and configs call `data_has_dict()` to skip dictionary-required cases.

State and persistence: It declares the external `data` list and cache lifecycle but stores no state itself. Callers are responsible for honoring ownership rules: buffers returned from read/create functions must be freed, and cache-derived paths are valid after successful initialization until `data_finish()`.

Dependencies and integration points: Uses standard `stddef.h` and `stdint.h`. It is included by `config.h`, `method.h`, `test.c`, and implementation modules.

Risks and test signals: The comments state `data_buffers_free()` frees a list of buffers, but callers must understand whether individual buffer contents are freed by the implementation. Directory versus file semantics are important: `data_buffer_get_data()` returns empty for directories. Correct use is signaled by non-empty `data_buffers_t` for datasets and successful dictionary loads only when `data_has_dict()` is true.
