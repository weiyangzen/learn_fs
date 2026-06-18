# sources/distributed-fs/ceph-client/include/linux/mfd/stm32-lptimer.h

## Purpose

This 99-line header defines STM32 low-power timer register offsets, bitfields, hardware feature bits, and parent data shared by LPTIMER child drivers.

## Important APIs, Types, and Functions

It exports `STM32_LPTIM_*` register offsets, ISR/ICR/IER/CR/CFGR/ARR/CCMR/HWCFGR/VERR bits, compare/update ready masks for MP15/MP25 variants, clock polarity constants, max auto-reload value, and `struct stm32_lptimer` with clock, regmap, encoder support, capture/compare channel count, and version.

## Control Flow

No code executes. Child drivers use parent-provided regmap and feature flags to configure counter, PWM, trigger, encoder, and capture/compare operations.

## State and Persistence Behavior

Hardware counter, compare, autoreload, interrupt, and configuration state persists in LPTIM registers. `struct stm32_lptimer` stores runtime parent-discovered capabilities.

## Dependencies and Integration Points

It includes clock and regmap headers and integrates STM32 MFD parent code with PWM, counter, trigger, and IIO/timer child devices.

## Risks and Edge Cases

MP25 adds different ready bits and extra compare/channel registers; drivers must check version/capabilities. Auto-reload is 16-bit. Update-ready bits must be observed before dependent writes.

## Test Signals

Build tests, variant capability detection tests, ARR/CMP update-ready timeout tests, encoder-channel tests, and PWM/counter hardware smoke tests.
