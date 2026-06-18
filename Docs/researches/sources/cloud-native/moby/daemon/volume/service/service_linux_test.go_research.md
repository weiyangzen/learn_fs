# sources/cloud-native/moby/daemon/volume/service/service_linux_test.go

## Purpose
Linux-specific API service test for local volume size reporting.

## Important APIs, Types, And Functions
`TestLocalVolumeSize` exercises `VolumesService.LocalVolumesSize`.

## Control Flow
The test creates a real local driver, registers it as the default driver plus a fake driver, creates two local volumes and one fake volume, writes different data sizes into local mountpoints, requests local sizes, and asserts only the two local volumes are returned with expected sizes and reference counts.

## State And Persistence
Uses temporary local volume directories and writes test data files.

## Dependencies And Integration Points
Validates service conversion, local driver, store references, directory size calculation, and filtering of non-local drivers.

## Risks
Directory size calculations can vary with filesystem behavior, but the test uses simple file contents to keep expectations stable.

## Test Signals
Good signal for `LocalVolumesSize` filtering and usage data population.
