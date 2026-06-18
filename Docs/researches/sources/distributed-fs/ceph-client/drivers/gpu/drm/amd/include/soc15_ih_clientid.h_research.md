# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc15_ih_clientid.h

## Purpose

`soc15_ih_clientid.h` defines interrupt-handler client IDs for SOC15/Vega10+ hardware and for SOC21 hardware. These IDs identify which hardware client generated an interrupt vector. AMDGPU interrupt registration and dispatch use the IDs with source IDs to route interrupts to the correct `amdgpu_irq_src` handler.

## Important APIs, Types, And Constants

- `enum soc15_ih_clientid` covers base Vega10+ client IDs from `SOC15_IH_CLIENTID_IH = 0x00` through `SOC15_IH_CLIENTID_MP1 = 0x1f`, followed by `SOC15_IH_CLIENTID_MAX`.
- SOC15 aliases after `SOC15_IH_CLIENTID_MAX` express hardware naming reuse:
  - `SOC15_IH_CLIENTID_VCN = SOC15_IH_CLIENTID_UVD`;
  - `SOC15_IH_CLIENTID_VCN1 = SOC15_IH_CLIENTID_UVD1`;
  - `SOC15_IH_CLIENTID_SDMA2 = SOC15_IH_CLIENTID_ACP`;
  - `SOC15_IH_CLIENTID_SDMA3 = SOC15_IH_CLIENTID_DCE`;
  - `SOC15_IH_CLIENTID_SDMA3_Sienna_Cichlid = SOC15_IH_CLIENTID_ISP`;
  - `SOC15_IH_CLIENTID_SDMA4 = SOC15_IH_CLIENTID_ISP`;
  - `SOC15_IH_CLIENTID_SDMA5 = SOC15_IH_CLIENTID_VCE0`;
  - `SOC15_IH_CLIENTID_SDMA6 = SOC15_IH_CLIENTID_XDMA`;
  - `SOC15_IH_CLIENTID_SDMA7 = SOC15_IH_CLIENTID_VCE1`;
  - `SOC15_IH_CLIENTID_VMC1 = SOC15_IH_CLIENTID_PCIE0`.
- `extern const char *soc15_ih_clientid_name[];` declares the debug-name table implemented in `amdgpu/amdgpu_irq.c`.
- `enum soc21_ih_clientid` defines a smaller SOC21-specific ID set with names such as `SOC21_IH_CLIENTID_DCN`, `SOC21_IH_CLIENTID_GFX`, `SOC21_IH_CLIENTID_IMU`, `SOC21_IH_CLIENTID_VPE`, `SOC21_IH_CLIENTID_LSDMA`, `SOC21_IH_CLIENTID_MP0`, and `SOC21_IH_CLIENTID_MP1`.

## Control Flow And Data Flow

The header itself has no functions. At runtime, IH ring decoding populates `struct amdgpu_iv_entry::client_id` and `src_id`. The interrupt dispatch path checks `client_id` against `AMDGPU_IRQ_CLIENTID_MAX`, which is defined as `SOC15_IH_CLIENTID_MAX` in `amdgpu_irq.h`, and then indexes `adev->irq.client[client_id].sources[src_id]`. IP blocks register handlers with calls such as `amdgpu_irq_add_id(adev, SOC15_IH_CLIENTID_VCN, src_id, source)` or SOC21 equivalents.

The name table in `amdgpu_irq.c` mirrors the base SOC15 enum order and is used in diagnostics such as VM fault messages. The comment in this header explicitly warns that updates to the enum must also update that name table.

## State And Persistence Behavior

The enums define compiled-in interrupt ABI values. Runtime state lives outside this header:

- decoded IV entries carry the numeric `client_id`;
- `adev->irq.client[]` stores registered handler arrays by client ID;
- `soc15_ih_clientid_name[]` provides read-only diagnostic labels.

No data is persisted by this header, but the numeric values must match hardware interrupt vector encodings.

## Dependencies

- Included by `amdgpu_irq.h`, which sets `AMDGPU_IRQ_CLIENTID_MAX` to `SOC15_IH_CLIENTID_MAX` and sizes `struct amdgpu_irq::client`.
- Implemented name dependency in `amdgpu_irq.c`; enum ordering and table ordering must stay synchronized.
- Used by IH implementations and IP blocks including VCN/JPEG, GMC, GFX, SDMA, NBIF, and virtualization paths when registering or decoding interrupts.
- SOC21 constants are consumed by newer IP code even though `AMDGPU_IRQ_CLIENTID_MAX` remains tied to the SOC15 max value; the SOC21 IDs still fit in the same 0x00-0x1f range represented by the SOC15 max.

## Integration Points

Primary integration is AMDGPU IRQ registration and dispatch:

- `amdgpu_irq_add_id()` registers a source handler under a `(client_id, src_id)` tuple.
- `amdgpu_irq_dispatch()` decodes an interrupt vector, validates the client and source IDs, handles legacy/ISP virtual IRQ shortcuts, and invokes the registered source callback.
- GMC VM fault code uses `entry->client_id` to classify fault source hubs and log readable client names.
- SDMA code maps engine instances to SOC15 client aliases, including Sienna Cichlid-specific SDMA3 behavior.

## Risks And Edge Cases

- Enum order is ABI-sensitive. Reordering base SOC15 entries breaks `soc15_ih_clientid_name[]`, handler registration arrays, and interrupt dispatch.
- Aliases mean several logical IP names share the same numeric client ID. Dispatch code cannot distinguish them by client ID alone; it must also use source ID, ASIC version, or engine instance context.
- `SOC15_IH_CLIENTID_MAX` is placed before aliases. This is intentional for array sizing; moving aliases before `MAX` would increase `AMDGPU_IRQ_CLIENTID_MAX` and could alter table expectations.
- SOC21 has sparse values with no entries for some SOC15 clients. Code shared between SOC15 and SOC21 must not blindly print SOC21 client IDs through the SOC15 name table unless the name collision is acceptable.
- The special case in interrupt dispatch for `SOC15_IH_CLIENTID_ISP` means aliases that equal ISP, such as SDMA3 Sienna Cichlid or SDMA4, can follow the virtual IRQ path under some conditions.

## Test Signals

- Compile coverage catches missing enum names in IP blocks.
- IRQ registration logs and runtime interrupt handling should show no "Invalid client_id", "Unregistered interrupt client_id", or "Unregistered interrupt src_id" messages for supported hardware.
- VCN/JPEG, SDMA, GFX, GMC VM fault, hotplug/vblank, and PSP/SMU interrupt paths are useful runtime smoke tests because they register and dispatch different client IDs.
- Fault injection or debug traces that decode IH vectors can validate that `soc15_ih_clientid_name[]` labels match the numeric client IDs.
