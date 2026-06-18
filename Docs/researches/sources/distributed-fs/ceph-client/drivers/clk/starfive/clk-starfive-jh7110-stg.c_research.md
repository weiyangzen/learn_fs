# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-stg.c

## Purpose
This module registers JH7110 System-Top-Group clocks for HIFI4, USB, PCIe, security, matrix/interconnect, E24, and DMA-related domains.

## Important APIs, Types, And Functions
`jh7110_stgclk_data[]` encodes all local STG gates/dividers. `jh7110_stgcrg_probe()` maps registers, registers each clock through the shared JH71x0 core, adds the OF provider, and registers reset auxiliary device `rst-stg`.

## Control Flow
Probe resolves local parents or firmware-named external parents from a compact `fw_name[]` array (`osc`, `hifi4_core`, `stg_axiahb`, `usb_125m`, `cpu_bus`, `hifi4_axi`, `nocstg_bus`, `apb_bus`). After successful clock provider registration it exposes reset ID 2.

## State And Persistence
State lives in STG clock registers and the allocated `jh71x0_clk_priv`. Several matrix clocks are `CLK_IS_CRITICAL` to keep interconnect paths running.

## Dependencies And Integration Points
It depends on the SYS clock controller for most top-level parents and reset helper export. Consumers include USB, PCIe, security, HIFI4, E24, and DMA drivers.

## Risks
Wrong external parent names break probe deferral or produce orphan clocks. Critical matrix clocks must remain enabled; changing their flags can hang bus access. Module ordering depends on SYS being available.

## Test Signals
USB and PCIe bring-up, security DMA clocks, reset-controller registration, critical clock retention, and module probe with all firmware parents available are primary checks.
