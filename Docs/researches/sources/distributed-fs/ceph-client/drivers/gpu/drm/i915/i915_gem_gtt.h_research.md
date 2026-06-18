# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_gtt.h

## Purpose
This header declares common GTT page-preparation and address-space allocation helpers and defines pin/bind placement flags shared across GEM/VMA code.

## Important APIs, Types, and Functions
It declares `i915_gem_gtt_prepare_pages()`, `i915_gem_gtt_finish_pages()`, `i915_gem_gtt_reserve()`, and `i915_gem_gtt_insert()`. It defines `I915_COLOR_UNEVICTABLE` and flags `PIN_NOEVICT`, `PIN_NOSEARCH`, `PIN_NONBLOCK`, `PIN_MAPPABLE`, `PIN_ZONE_4G`, `PIN_HIGH`, `PIN_OFFSET_BIAS`, `PIN_OFFSET_FIXED`, `PIN_OFFSET_GUARD`, `PIN_VALIDATE`, `PIN_GLOBAL`, `PIN_USER`, and `PIN_OFFSET_MASK`.

## Control Flow
No executable flow is present. Callers pass flags into VMA pin/bind and GTT insertion paths to control search, eviction, mappable placement, fixed offsets, guard pages, validation-only behavior, and global/user binding.

## State and Persistence Behavior
The header stores no state. Its constants influence persistent VMA/node placement and binding flags.

## Dependencies and Integration Points
It includes IO mapping, `drm_mm`, Intel GTT constants, and i915 scatterlist helpers. It is consumed by GEM object, VMA, execbuf, eviction, and error-capture code.

## Risks
Flag values are ABI internal but widely shared; changing them breaks bitmask users. `PIN_OFFSET_MASK` overlaps low address bits by design and must stay aligned with GTT page masks. `I915_COLOR_UNEVICTABLE` is used to protect non-VMA nodes from eviction.

## Test Signals
Build coverage plus GTT/VMA selftests for each flag combination and unevictable-color behavior.
