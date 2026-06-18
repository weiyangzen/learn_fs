<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/aws/snapshotter_bench_cf.yml -->
# sources/cloud-native/containerd/contrib/aws/snapshotter_bench_cf.yml

## Purpose
CloudFormation template for launching an EC2 host with EBS volumes for snapshotter benchmarking.

## Important APIs, Types, And Functions
Defines parameters for key, AMI, security groups, instance type, volume IOPS/size/type, and resources for EC2 plus block devices.

## Control Flow
CloudFormation provisions an EBS-optimized instance with root and multiple benchmark volumes, including a device-mapper thin-pool-oriented volume.

## State And Persistence
Creates AWS EC2/EBS infrastructure and associated costs until deleted.

## Dependencies And Integration Points
AWS CloudFormation/EC2/EBS, Amazon Linux 2 AMI assumption, SSH security groups.

## Risks And Test Signals
Default AMI and instance type may be obsolete; running template incurs spend. Validation is stack creation/manual benchmark run. Source size reviewed: 144 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/aws/snapshotter_bench_cf.yml -->
