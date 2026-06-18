# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/class.h

## Purpose
Centralizes NVIF internal class IDs and NVIDIA-assigned hardware/software class numbers used for object construction and class matching.

## Important APIs, Types, And Functions
Defines NVIF private classes for client/control/MMU/mem/VMM/event/display/channel objects, device/DMA/display/channel classes, 2D/M2MF/copy/video/compute/graphics classes, usermode classes, display core/window/cursor classes through GB202, and Blackwell additions.

## Control Flow
No executable flow. Class-selection helpers such as `nvif_mclass()` compare requested class IDs and versions against supported-class lists.

## State And Persistence
No state. Values become ABI object class identifiers in NVIF ioctls and hardware channel object bindings.

## Dependencies And Integration Points
Included by object constructors, channel/display/device setup, and class-specific push or method payload code.

## Risks
IDs are ABI-sensitive. A wrong class number can instantiate the wrong engine object or fail on supported hardware. Private negative IDs must not collide with hardware IDs.

## Test Signals
Successful object construction across GPU generations, supported-class matching, and feature probe logs validate correctness.
