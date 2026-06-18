## sources/distributed-fs/ceph-client/drivers/dma/acpi-dma.c

### Purpose
`acpi-dma.c` provides ACPI-side DMA controller registration and slave-channel lookup helpers. It lets DMA controller drivers register translation callbacks and lets ACPI-enumerated client devices request channels by FixedDMA descriptor index or name.

### Important APIs, Types, And Functions
Exported APIs are `acpi_dma_controller_register()`, `acpi_dma_controller_free()`, `devm_acpi_dma_controller_register()`, `acpi_dma_request_slave_chan_by_index()`, `acpi_dma_request_slave_chan_by_name()`, and `acpi_dma_simple_xlate()`. Important internals include global `acpi_dma_list`, `acpi_dma_lock`, `acpi_dma_parse_csrt()`, `acpi_dma_parse_resource_group()`, `acpi_dma_update_dma_spec()`, and `acpi_dma_parse_fixed_dma()`.

### Control Flow, State, And Persistence
Controller registration validates the ACPI companion, allocates `struct acpi_dma`, stores the translation callback and driver data, optionally parses CSRT to discover controller-relative request-line ranges and DMA mask, then appends the controller to a global list. Client lookup parses FixedDMA resources into channel/request IDs, walks registered controllers under the mutex, adjusts request lines to controller-relative IDs when CSRT ranges are available, and invokes the controller's xlate function. Name lookup uses `dma-names` when present and falls back to conventional `tx` index 0 and `rx` index 1.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include ACPI resource parsing, CSRT tables, device properties, DMA masks, `dma_request_channel()`, and `linux/acpi_dma.h`. Integration points are ACPI-aware DMA controller drivers and client drivers using common channel request helpers. Risks include incomplete CSRT data, GSI registration side effects while matching IRQs, request-line range mismatches producing `-EPROBE_DEFER`, global list lifetime under device detach, and fallback name assumptions. Test signals include controller register/free/devm unwind, FixedDMA index and name lookup, CSRT present/absent paths, request line rebasing, invalid ACPI companions, and deferred probe when no controller has registered yet.
